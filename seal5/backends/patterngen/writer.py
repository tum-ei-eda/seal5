# SPDX-License-Identifier: Apache-2.0
#
# This file is part of the M2-ISA-R project: https://github.com/tum-ei-eda/M2-ISA-R
#
# Copyright (C) 2022
# Chair of Electrical Design Automation
# Technical University of Munich

"""Clean M2-ISA-R/Seal5 metamodel to .core_desc file."""

import os
import argparse
import logging
import pathlib
import pickle
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import Union

from m2isar.metamodel import arch

from seal5.tools import cdsl2llvm
from seal5.index import write_index_yaml, File, NamedPatch
from seal5.model import Seal5InstrAttribute

logger = logging.getLogger("patterngen_tablegen_writer")


def main():
    """Main app entrypoint."""

    # read command line args
    parser = argparse.ArgumentParser()
    parser.add_argument("top_level", help="A .m2isarmodel or .seal5model file.")
    parser.add_argument("--log", default="info", choices=["critical", "error", "warning", "info", "debug"])
    parser.add_argument("--output", "-o", type=str, default=None)
    parser.add_argument("--splitted", action="store_true", help="Split per set and instruction")
    parser.add_argument("--formats", action="store_true", help="Also generate instruction formats")
    parser.add_argument("--patterns", action="store_true", help="Also generate instruction patterns")
    parser.add_argument("--metrics", default=None, help="Output metrics to file")
    parser.add_argument("--index", default=None, help="Output index to file")
    parser.add_argument("--ext", type=str, default="td", help="Default file extension (if using --splitted)")
    parser.add_argument("--parallel", type=int, default=1, help="How many instructions should be processed in parallel")
    # parser.add_argument("--xlen", type=int, default=32, help="RISC-V XLEN")
    args = parser.parse_args()

    # initialize logging
    logging.basicConfig(level=getattr(logging, args.log.upper()))

    # resolve model paths
    top_level = pathlib.Path(args.top_level)
    # abs_top_level = top_level.resolve()

    is_seal5_model = False
    # print("top_level", top_level)
    # print("suffix", top_level.suffix)
    if top_level.suffix == ".seal5model":
        is_seal5_model = True
    if args.output is None:
        assert top_level.suffix in [".m2isarmodel", ".seal5model"], "Can not infer model type from file extension."
        raise NotImplementedError

        # out_path = top_level.parent / (top_level.stem + ".core_desc")
    else:
        out_path = pathlib.Path(args.output)

    logger.info("loading models")
    if not is_seal5_model:
        raise NotImplementedError

    # load models
    with open(top_level, "rb") as f:
        # models: "dict[str, arch.CoreDef]" = pickle.load(f)
        if is_seal5_model:
            model: "dict[str, Union[arch.InstructionSet, ...]]" = pickle.load(f)
            model["cores"] = {}
        else:  # TODO: core vs. set!
            temp: "dict[str, Union[arch.InstructionSet, arch.CoreDef]]" = pickle.load(f)
            assert len(temp) > 0, "Empty model!"
            if isinstance(list(temp.values())[0], arch.CoreDef):
                model = {"cores": temp, "sets": {}}
            elif isinstance(list(temp.values())[0], arch.InstructionSet):
                model = {"sets": temp, "cores": {}}
            else:
                assert False

    metrics = {
        "n_sets": 0,
        "n_instructions": 0,
        "n_skipped": 0,
        "n_failed": 0,
        "n_success": 0,
    }
    # preprocess model
    # print("model", model)
    artifacts = {}
    artifacts[None] = []  # used for global artifacts
    settings = model.get("settings", None)
    if args.splitted:
        # errs = []
        # model_includes = []
        default_mattr = "+m,+fast-unaligned-access"
        if settings:
            riscv_settings = settings.riscv
            if riscv_settings:
                features = riscv_settings.features
                if features is None:
                    pass
                else:
                    default_mattr = ",".join([f"+{f}" for f in features])

        assert out_path.is_dir(), "Expecting output directory when using --splitted"
        for set_name, set_def in model["sets"].items():
            xlen = set_def.xlen
            artifacts[set_name] = []
            metrics["n_sets"] += 1
            ext_settings = set_def.settings
            set_dir = out_path / set_name
            includes = []

            def process_instrunction(instr_def):
                metrics["n_instructions"] += 1
                input_file = out_path / set_name / f"{instr_def.name}.core_desc"
                attrs = instr_def.attributes
                if len(attrs) > 0:
                    skip = False
                    if Seal5InstrAttribute.MAY_LOAD in attrs:
                        skip = True
                    elif Seal5InstrAttribute.MAY_STORE in attrs:
                        skip = True
                    elif arch.InstrAttribute.COND in attrs:
                        skip = True
                    elif arch.InstrAttribute.NO_CONT in attrs:
                        skip = True
                    if skip:
                        metrics["n_skipped"] += 1
                        return False
                if not input_file.is_file():
                    metrics["n_skipped"] += 1
                    return False
                # if args.patterns:
                out_name = f"{instr_def.name}.{args.ext}"
                output_file = set_dir / out_name
                if args.formats:
                    out_name_fmt = f"{instr_def.name}InstrFormat.{args.ext}"
                    output_file_fmt = set_dir / out_name_fmt
                install_dir = os.getenv("CDSL2LLVM_DIR", None)
                predicate = None
                mattr = default_mattr
                if ext_settings is not None:
                    predicate = ext_settings.get_predicate(name=set_name)
                    arch_ = ext_settings.get_arch(name=set_name)
                    mattr = ",".join([*mattr.split(","), f"+{arch_}"])
                if xlen == 64 and "+64bit" not in mattr:
                    mattr = ",".join([*mattr.split(","), "+64bit"])

                assert install_dir is not None
                install_dir = pathlib.Path(install_dir)
                try:
                    cdsl2llvm.run_pattern_gen(
                        # install_dir / "llvm" / "build",
                        install_dir,
                        input_file,
                        output_file,
                        skip_patterns=not args.patterns,
                        skip_formats=not args.formats,
                        ext=predicate,
                        mattr=mattr,
                        xlen=xlen,
                    )
                    if output_file.is_file():
                        metrics["n_success"] += 1
                        if args.formats:
                            file_artifact_fmt_dest = f"llvm/lib/Target/RISCV/seal5/{set_name}/{out_name_fmt}"
                            file_artifact_fmt = File(file_artifact_fmt_dest, src_path=output_file_fmt)
                            artifacts[set_name].append(file_artifact_fmt)
                            include_path_fmt = f"{set_name}/{out_name_fmt}"
                            includes.append(include_path_fmt)
                        if args.patterns:
                            file_artifact_dest = f"llvm/lib/Target/RISCV/seal5/{set_name}/{out_name}"
                            file_artifact = File(file_artifact_dest, src_path=output_file)
                            artifacts[set_name].append(file_artifact)
                            include_path = f"{set_name}/{out_name}"
                            includes.append(include_path)
                    else:
                        metrics["n_failed"] += 1
                except AssertionError:
                    metrics["n_failed"] += 1
                    # errs.append((insn_name, str(ex)))
                return True

            with ThreadPoolExecutor(args.parallel) as executor:
                futures = []
                for instr_def in set_def.instructions.values():
                    future = executor.submit(process_instrunction, instr_def)
                    futures.append(future)
                results = []
                for future in as_completed(futures):
                    result = future.result
                    results.append(result)
            if len(includes) > 0:
                set_includes_str = "\n".join([f'include "seal5/{inc}"' for inc in includes])
                set_includes_artifact_dest = f"llvm/lib/Target/RISCV/seal5/{set_name}.td"
                set_name_lower = set_name.lower()
                key = f"{set_name_lower}_set_td_includes"
                set_includes_artifact = NamedPatch(set_includes_artifact_dest, key=key, content=set_includes_str)
                artifacts[set_name].append(set_includes_artifact)
                # model_includes.append(f"{set_name}.td")
        # if len(model_includes) > 0:
        #     model_includes_str = "\n".join([f'include "seal5/{inc}"' for inc in model_includes])
        #     model_includes_artifact_dest = "llvm/lib/Target/RISCV/seal5.td"
        #     key = "seal5_td_includes"
        #     model_includes_artifact = NamedPatch(model_includes_artifact_dest, key, content=model_includes_str)
        #     artifacts[None].append(model_includes_artifact)
        # if len(errs) > 0:
        #     # print("errs", errs)
        #     for insn_name, err_str in errs:
        #         print("Err:", insn_name, err_str)
        #         input("!")
        #         cdsl2llvm.
        #         out_path_ = out_path / set_name / f"{instr_def.name}.{args.ext}"
        #         out_path_.parent.mkdir(exist_ok=True)
    else:
        raise NotImplementedError
    if args.metrics:
        metrics_file = args.metrics
        with open(metrics_file, "w") as f:
            f.write(",".join(metrics.keys()))
            f.write("\n")
            f.write(",".join(map(str, metrics.values())))
            f.write("\n")
    if args.index:
        if sum(map(lambda x: len(x), artifacts.values())) > 0:
            global_artifacts = artifacts.get(None, [])
            set_artifacts = {key: value for key, value in artifacts.items() if key is not None}
            index_file = args.index
            write_index_yaml(index_file, global_artifacts, set_artifacts, content=True)
        else:
            logger.warning("No patches generated. No index file will be written.")


if __name__ == "__main__":
    main()

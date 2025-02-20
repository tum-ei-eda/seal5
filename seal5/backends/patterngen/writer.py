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
from concurrent.futures import ThreadPoolExecutor, as_completed

import pandas as pd

from seal5.tools import cdsl2llvm
from seal5.index import write_index_yaml, File, NamedPatch
from seal5.model import Seal5InstrAttribute
from seal5.riscv_utils import build_riscv_mattr, get_riscv_defaults
from seal5.model_utils import load_model

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
    parser.add_argument("--compat", action="store_true")
    # parser.add_argument("--xlen", type=int, default=32, help="RISC-V XLEN")
    args = parser.parse_args()

    # initialize logging
    logging.basicConfig(level=getattr(logging, args.log.upper()))

    # resolve model paths
    top_level = pathlib.Path(args.top_level)
    out_path = pathlib.Path(args.output)
    model_name = top_level.stem

    model_obj = load_model(top_level, compat=args.compat)

    metrics = {
        "n_sets": 0,
        "n_instructions": 0,
        "n_skipped": 0,
        "n_failed": 0,
        "n_success": 0,
        "skipped_instructions": [],
        "failed_instructions": [],
        "success_instructions": [],
    }
    # preprocess model
    # print("model", model)
    artifacts = {}
    artifacts[None] = []  # used for global artifacts
    settings = model_obj.settings
    if args.splitted:
        # errs = []
        # model_includes = []
        if settings:
            riscv_settings = settings.riscv
            model_settings = settings.models.get(model_name)
            model_riscv_settings = model_settings.riscv
            if model_riscv_settings is not None:
                riscv_settings = riscv_settings.merge(model_riscv_settings)
        else:
            riscv_settings = None

        assert out_path.is_dir(), "Expecting output directory when using --splitted"
        for set_name, set_def in model_obj.sets.items():
            xlen = set_def.xlen
            artifacts[set_name] = []
            metrics["n_sets"] += 1
            set_dir = out_path / set_name
            ext_settings = set_def.settings
            riscv_settings_ = riscv_settings
            ext_riscv_settings = ext_settings.riscv
            if ext_riscv_settings is not None:
                riscv_settings_ = riscv_settings_.merge(ext_riscv_settings)
            default_features, default_xlen = get_riscv_defaults(riscv_settings)
            if xlen is None:  # TODO: redundant?
                xlen = default_xlen

            predicate = None
            features = [*default_features]
            if ext_settings is not None:
                predicate = ext_settings.get_predicate(name=set_name)
                arch_ = ext_settings.get_arch(name=set_name)
                if arch_ is not None:
                    features.append(arch_)

            mattr = build_riscv_mattr(features, xlen)

            def process_instrunction(instr_def, set_name, set_dir, mattr, predicate, xlen):
                includes_ = []
                metrics["n_instructions"] += 1
                input_file = out_path / set_name / f"{instr_def.name}.core_desc"
                attrs = instr_def.attributes
                skip = False
                if len(attrs) > 0:
                    skip = Seal5InstrAttribute.SKIP_PATTERN_GEN in attrs
                if not input_file.is_file():
                    skip = True
                if skip:
                    metrics["n_skipped"] += 1
                    metrics["skipped_instructions"].append(instr_def.name)
                    return False, includes_
                # if args.patterns:
                out_name = f"{instr_def.name}.{args.ext}"
                output_file = set_dir / out_name
                if args.formats:
                    out_name_fmt = f"{instr_def.name}InstrFormat.{args.ext}"
                    output_file_fmt = set_dir / out_name_fmt
                install_dir = os.getenv("CDSL2LLVM_DIR", None)

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
                        metrics["success_instructions"].append(instr_def.name)
                        if args.formats:
                            file_artifact_fmt_dest = f"llvm/lib/Target/RISCV/seal5/{set_name}/{out_name_fmt}"
                            file_artifact_fmt = File(file_artifact_fmt_dest, src_path=output_file_fmt)
                            artifacts[set_name].append(file_artifact_fmt)
                            include_path_fmt = f"{set_name}/{out_name_fmt}"
                            includes_.append(include_path_fmt)
                        if args.patterns:
                            file_artifact_dest = f"llvm/lib/Target/RISCV/seal5/{set_name}/{out_name}"
                            file_artifact = File(file_artifact_dest, src_path=output_file)
                            artifacts[set_name].append(file_artifact)
                            include_path = f"{set_name}/{out_name}"
                            includes_.append(include_path)
                    else:
                        metrics["n_failed"] += 1
                        metrics["failed_instructions"].append(instr_def.name)
                except AssertionError:
                    metrics["n_failed"] += 1
                    metrics["failed_instructions"].append(instr_def.name)
                    return False, includes_
                    # errs.append((insn_name, str(ex)))
                return True, includes_

            includes = []
            with ThreadPoolExecutor(args.parallel) as executor:
                futures = []
                for instr_def in set_def.instructions.values():
                    future = executor.submit(process_instrunction, instr_def, set_name, set_dir, mattr, predicate, xlen)
                    futures.append(future)
                results = []
                for future in as_completed(futures):
                    result_, includes_ = future.result()
                    results.append(result_)
                    if result_:
                        includes.extend(includes_)
            if len(includes) > 0:
                set_includes_str = "\n".join([f'include "seal5/{inc}"' for inc in includes])
                if len(set_includes_str.strip()) > 0:
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
        metrics_df = pd.DataFrame({key: [val] for key, val in metrics.items()})
        metrics_df.to_csv(metrics_file, index=False)
    if args.index:
        if sum(map(len, artifacts.values())) > 0:
            global_artifacts = artifacts.get(None, [])
            set_artifacts = {key: value for key, value in artifacts.items() if key is not None}
            index_file = args.index
            write_index_yaml(index_file, global_artifacts, set_artifacts, content=True)
        else:
            logger.warning("No patches generated. No index file will be written.")


if __name__ == "__main__":
    main()

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
from typing import Union

from m2isar.metamodel import arch

import pandas as pd

from seal5.tools import cdsl2llvm
from seal5.model import Seal5InstrAttribute
from seal5.riscv_utils import build_riscv_mattr, get_riscv_defaults

logger = logging.getLogger("llvmir_behavior_writer")


def main():
    """Main app entrypoint."""

    # read command line args
    parser = argparse.ArgumentParser()
    parser.add_argument("top_level", help="A .m2isarmodel or .seal5model file.")
    parser.add_argument("--log", default="info", choices=["critical", "error", "warning", "info", "debug"])
    parser.add_argument("--output", "-o", type=str, default=None)
    parser.add_argument("--splitted", action="store_true", help="Split per set and instruction")
    parser.add_argument("--metrics", default=None, help="Output metrics to file")
    parser.add_argument("--ext", type=str, default="ll", help="Default file extension (if using --splitted)")
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
    if args.output is not None:
        out_path = pathlib.Path(args.output)
    else:
        assert top_level.suffix in [".m2isarmodel", ".seal5model"], "Can not infer model type from file extension."
        # out_path = top_level.parent / (top_level.stem + ".core_desc")
        raise NotImplementedError

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

    # preprocess model
    # print("model", model)
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
    settings = model.get("settings", None)
    if args.splitted:
        # errs = []
        # model_includes = []
        # errs = []
        if settings:
            riscv_settings = settings.riscv
        else:
            riscv_settings = None
        default_features, default_xlen = get_riscv_defaults(riscv_settings)

        assert out_path.is_dir(), "Expecting output directory when using --splitted"
        for set_name, set_def in model["sets"].items():
            xlen = set_def.xlen
            if xlen is None:
                xlen = default_xlen
            metrics["n_sets"] += 1
            ext_settings = set_def.settings
            for instr_def in set_def.instructions.values():
                metrics["n_instructions"] += 1
                attrs = instr_def.attributes
                if len(attrs) > 0:
                    skip = False
                    if instr_def.size != 32:
                        skip = True
                    elif len(attrs.get(Seal5InstrAttribute.USES, [])) > 0:
                        skip = True
                    elif len(attrs.get(Seal5InstrAttribute.DEFS, [])) > 0:
                        skip = True
                    elif Seal5InstrAttribute.MAY_LOAD in attrs:
                        skip = True
                    elif Seal5InstrAttribute.MAY_STORE in attrs:
                        skip = True
                    elif arch.InstrAttribute.COND in attrs:
                        skip = True
                    elif arch.InstrAttribute.NO_CONT in attrs:
                        skip = True
                    if skip:
                        metrics["n_skipped"] += 1
                        metrics["skipped_instructions"].append(instr_def.name)
                        continue
                input_file = out_path / set_name / f"{instr_def.name}.core_desc"
                if not input_file.is_file():
                    metrics["n_skipped"] += 1
                    metrics["skipped_instructions"].append(instr_def.name)
                    # errs.append(TODO)
                output_file = out_path / set_name / f"{instr_def.name}.{args.ext}"

                features = [*default_features]
                if ext_settings is not None:
                    arch_ = ext_settings.get_arch(name=set_name)
                    if arch is not None:
                        features.append(arch_)
                mattr = build_riscv_mattr(features, xlen)

                install_dir = os.getenv("CDSL2LLVM_DIR", None)
                assert install_dir is not None
                install_dir = pathlib.Path(install_dir)
                try:
                    cdsl2llvm.run_pattern_gen(
                        # install_dir / "llvm" / "build",
                        install_dir,
                        input_file,
                        output_file,
                        skip_patterns=True,
                        skip_formats=True,
                        mattr=mattr,
                        xlen=xlen,
                    )
                    metrics["n_success"] += 1
                    metrics["success_instructions"].append(instr_def.name)
                except AssertionError:
                    metrics["n_failed"] += 1
                    metrics["failed_instructions"].append(instr_def.name)
                    # errs.append((insn_name, str(ex)))
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


if __name__ == "__main__":
    main()

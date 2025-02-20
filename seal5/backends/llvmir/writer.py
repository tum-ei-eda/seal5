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

import pandas as pd

from seal5.tools import cdsl2llvm
from seal5.model import Seal5InstrAttribute
from seal5.riscv_utils import build_riscv_mattr, get_riscv_defaults
from seal5.model_utils import load_model

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
    parser.add_argument("--compat", action="store_true")
    args = parser.parse_args()

    # initialize logging
    logging.basicConfig(level=getattr(logging, args.log.upper()))

    # resolve model paths
    top_level = pathlib.Path(args.top_level)
    out_path = pathlib.Path(args.output)
    model_name = top_level.stem

    model_obj = load_model(top_level, compat=args.compat)

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
    settings = model_obj.settings
    if args.splitted:
        # errs = []
        # model_includes = []
        # errs = []
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
            metrics["n_sets"] += 1
            ext_settings = set_def.settings
            riscv_settings_ = riscv_settings
            ext_riscv_settings = ext_settings.riscv
            if ext_riscv_settings is not None:
                riscv_settings_ = riscv_settings_.merge(ext_riscv_settings)
            default_features, default_xlen = get_riscv_defaults(riscv_settings)
            if xlen is None:  # TODO: redundant?
                xlen = default_xlen
            for instr_def in set_def.instructions.values():
                metrics["n_instructions"] += 1
                attrs = instr_def.attributes
                if len(attrs) > 0:
                    skip = Seal5InstrAttribute.SKIP_PATTERN_GEN in attrs
                    if skip:
                        metrics["n_skipped"] += 1
                        metrics["skipped_instructions"].append(instr_def.name)
                        continue
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
                    # errs.append(TODO)
                output_file = out_path / set_name / f"{instr_def.name}.{args.ext}"

                features = [*default_features]
                if ext_settings is not None:
                    arch_ = ext_settings.get_arch(name=set_name)
                    if arch_ is not None:
                        features.append(arch_)
                    riscv_settings = ext_settings.riscv
                    if riscv_settings is not None:
                        xlen_ = riscv_settings.xlen
                        if xlen_ is not None:
                            xlen = xlen_
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

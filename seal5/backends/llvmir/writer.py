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

from seal5.tools import cdsl2llvm

logger = logging.getLogger("llvmir_behavior_writer")


def main():
    """Main app entrypoint."""

    # read command line args
    parser = argparse.ArgumentParser()
    parser.add_argument("top_level", help="A .m2isarmodel or .seal5model file.")
    parser.add_argument("--log", default="info", choices=["critical", "error", "warning", "info", "debug"])
    parser.add_argument("--output", "-o", type=str, default=None)
    parser.add_argument("--splitted", action="store_true", help="Split per set and instruction")
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

    # preprocess model
    # print("model", model)
    if args.splitted:
        # errs = []
        assert out_path.is_dir(), "Expecting output directory when using --splitted"
        for set_name, set_def in model["sets"].items():
            for instr_def in set_def.instructions.values():
                input_file = out_path / set_name / f"{instr_def.name}.core_desc"
                if not input_file.is_file():
                    pass  # skipping
                    # errs.append(TODO)
                output_file = out_path / set_name / f"{instr_def.name}.{ext}"
                install_dir = os.getenv("CDSL2LLVM_DIR", None)
                assert install_dir is not None
                install_dir = pathlib.Path(install_dir)
                try:
                    cdsl2llvm.run_pattern_gen(install_dir / "llvm" / "build", input_file, output_file, skip_patterns=True, skip_formats=True)
                except AssertionError:
                    pass
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


if __name__ == "__main__":
    main()

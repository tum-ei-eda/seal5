# SPDX-License-Identifier: Apache-2.0
#
# This file is part of the M2-ISA-R project: https://github.com/tum-ei-eda/M2-ISA-R
#
# Copyright (C) 2022
# Chair of Electrical Design Automation
# Technical University of Munich

"""Clean M2-ISA-R/Seal5 metamodel to .core_desc file."""

import argparse
import logging
import pathlib

import yaml

from seal5.model_utils import load_model

from seal5.logging import Logger

logger = Logger("backends.yaml_writer")

# @dataclass
# class Seal5Settings(YAMLSettings):
#     extensions: Optional[Dict[str, ExtensionsSettings]] = None
# @dataclass
# class ExtensionsSettings(YAMLSettings):
#     feature: Optional[str] = None
#     arch: Optional[str] = None
#     version: Optional[str] = None
#     experimental: Optional[bool] = None
#     vendor: Optional[bool] = None
#     instructions: Optional[List[str]] = None
#     NEW: model
#     # patches


def main():
    """Main app entrypoint."""

    # read command line args
    parser = argparse.ArgumentParser()
    parser.add_argument("top_level", help="A .m2isarmodel or .seal5model file.")
    parser.add_argument("--log", default="info", choices=["critical", "error", "warning", "info", "debug"])
    parser.add_argument("--output", "-o", type=str, default=None)
    parser.add_argument("--compat", action="store_true")
    args = parser.parse_args()

    # initialize logging
    logger.setLevel(getattr(logging, args.log.upper()))

    # resolve model paths
    top_level = pathlib.Path(args.top_level)
    model_name = top_level.stem
    out_path = pathlib.Path(args.output)

    model_obj = load_model(top_level, compat=args.compat)

    # preprocess model
    # print("model", model)
    data = {"extensions": {}}
    for set_name, set_def in model_obj.sets.items():
        # print("set", set_def)
        is_group_set = False
        if len(set_def.instructions) == 0:
            assert len(set_def.extension) > 0
            is_group_set = True
        set_data = {"instructions": []}
        riscv_data = {}
        if is_group_set:
            # set_data["implies"] = set_def.extension
            set_data["requires"] = set_def.extension
        else:
            riscv_data["xlen"] = set_def.xlen
            set_data["riscv"] = riscv_data
        llvm_imm_types = set()
        for instr in set_def.instructions.values():
            set_data["instructions"].append(instr.name)
            llvm_imm_types.update(instr.llvm_imm_types)
        set_data["required_imm_types"] = list(llvm_imm_types)
        data["extensions"][set_name] = set_data
    data = {"models": {model_name: data}}
    with open(out_path, "w", encoding="utf-8") as f:
        yaml.dump(data, f)


if __name__ == "__main__":
    main()

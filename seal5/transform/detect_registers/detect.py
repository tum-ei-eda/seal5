# SPDX-License-Identifier: Apache-2.0
#
# This file is part of the M2-ISA-R project: https://github.com/tum-ei-eda/M2-ISA-R
#
# Copyright (C) 2022
# Chair of Electrical Design Automation
# Technical University of Munich

"""Detect available registers for Seal5."""

import sys
import argparse
import logging
import pathlib

import seal5.model as seal5_model
from seal5.model_utils import load_model, dump_model

logger = logging.getLogger("detect_registers")


def detect_registers(set_def: seal5_model.Seal5InstructionSet):
    to_skip = ["FENCE", "RES", "PRIV", "DPC"]  # TODO: eliminate unused memories during optimization?
    for mem_name, mem in set_def.memories.items():
        if mem_name in to_skip:
            continue
        if mem.is_main_mem or mem.is_pc:
            continue
        assert mem_name not in set_def.registers, "Registers already added to set."
        name = mem_name
        # print("name", name)
        size = mem.data_range.length
        # print("size", size)
        width = mem.size
        # print("width", width)
        # TODO: implement memory dtype in m2isar
        # assert mem.data_type in [arch.DataType.S, arch.DataType.U],
        #  f"Unsupported dtype {mem.data_type} for memory {mem_name}"
        # signed = mem.data_type == arch.DataType.S
        signed = False
        reg_class = seal5_model.Seal5RegisterClass.CUSTOM
        if name == "X":
            reg_class = seal5_model.Seal5RegisterClass.GPR
        elif name == "F":
            reg_class = seal5_model.Seal5RegisterClass.FPR
        elif name == "CSR":
            reg_class = seal5_model.Seal5RegisterClass.CSR
        if size is None:
            raise NotImplementedError(f"Register with unknown size: {name}")
        if size > 1:  # TODO: check this!
            names = [f"{name}{i}" for i in range(mem.data_range.lower, mem.data_range.upper + 1)]
            # print("names", names)
            group = seal5_model.Seal5RegisterGroup(names, size, width, signed, reg_class)
            # print("group", group)
            set_def.register_groups[name] = group
            for reg in group.registers:
                set_def.registers[reg.name] = reg
        else:
            reg = seal5_model.Seal5Register(name, size, width, signed, reg_class)
            # print("reg", reg)
            set_def.registers[name] = reg


def get_parser():
    # read command line args
    parser = argparse.ArgumentParser()
    parser.add_argument("top_level", help="A .m2isarmodel or .seal5model file.")
    parser.add_argument("--log", default="info", choices=["critical", "error", "warning", "info", "debug"])
    parser.add_argument("--output", "-o", type=str, default=None)
    parser.add_argument("--compat", action="store_true")
    return parser


def run(args):
    # initialize logging
    logging.basicConfig(level=getattr(logging, args.log.upper()))

    # resolve model paths
    top_level = pathlib.Path(args.top_level)

    out_path = (top_level.parent / top_level.stem) if args.output is None else args.output

    model_obj = load_model(top_level, compat=args.compat)

    to_skip = ["Zicsr"]  # TODO: use yaml!
    for set_name, set_def in model_obj.sets.items():
        if set_name in to_skip:
            continue
        logger.info("processing set %s", set_name)
        detect_registers(set_def)

    dump_model(model_obj, out_path, compat=args.compat)


def main(argv):
    parser = get_parser()
    args = parser.parse_args(argv)
    run(args)


if __name__ == "__main__":
    main(sys.argv[1:])

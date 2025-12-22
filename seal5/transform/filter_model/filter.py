# SPDX-License-Identifier: Apache-2.0
#
# This file is part of the M2-ISA-R project: https://github.com/tum-ei-eda/M2-ISA-R
#
# Copyright (C) 2022
# Chair of Electrical Design Automation
# Technical University of Munich

"""Filter M2-ISA-R/Seal5 metamodel."""

import re
import sys
import argparse
import logging
import pathlib

from m2isar.metamodel import arch

from seal5.model_utils import load_model, dump_model
from seal5.riscv_utils import OPCODE_LOOKUP


from seal5.logging import Logger

logger = Logger("transform.filter_model")


class DropUnusedContext:
    def __init__(self, names: "list[str]"):
        self.names = names
        self.to_keep = set()

    @property
    def to_drop(self):
        return set(name for name in self.names if name not in self.to_keep)

    def track(self, name: str):
        if name in self.names:
            # logger.debug("Tracked use of %s", name)
            self.to_keep.add(name)


def get_parser():
    # read command line args
    parser = argparse.ArgumentParser()
    parser.add_argument("top_level", help="A .m2isarmodel or .seal5model file.")
    parser.add_argument("--keep-sets", type=str, default=None)
    parser.add_argument("--drop-sets", type=str, default=None)
    parser.add_argument("--keep-instructions", type=str, default=None)
    parser.add_argument("--drop-instructions", type=str, default=None)
    parser.add_argument("--keep-opcodes", type=str, default=None)
    parser.add_argument("--drop-opcodes", type=str, default=None)
    parser.add_argument("--keep-encoding-sizes", type=str, default=None)
    parser.add_argument("--drop-encoding-sizes", type=str, default=None)
    # TODO: filter builtins/aliases
    parser.add_argument("--log", default="info", choices=["critical", "error", "warning", "info", "debug"])
    parser.add_argument("--output", "-o", type=str, default=None)
    parser.add_argument("--compat", action="store_true")
    return parser


def run(args):
    # initialize logging
    logger.setLevel(getattr(logging, args.log.upper()))

    # resolve model paths
    top_level = pathlib.Path(args.top_level)

    out_path = (top_level.parent / top_level.stem) if args.output is None else args.output

    model_obj = load_model(top_level, compat=args.compat)

    # preprocess model
    # print("model", model["sets"]["XCoreVMac"].keys())
    if args.keep_sets:
        keep_sets = args.keep_sets.split(",")
    else:
        keep_sets = []
    if args.drop_sets:
        drop_sets = args.drop_sets.split(",")
    else:
        drop_sets = []
    if args.keep_instructions:
        keep_instructions = args.keep_instructions.split(",")
    else:
        keep_instructions = []
    if args.drop_instructions:
        drop_instructions = args.drop_instructions.split(",")
    else:
        drop_instructions = []

    def opcodes_helper(x):
        try:
            x = int(x, 0)
        except ValueError as exc:
            x = OPCODE_LOOKUP.get(x, None)
            if x is None:
                raise ValueError(
                    f"Opcode lookup by string failed for {x}. Options: {list(OPCODE_LOOKUP.keys())}"
                ) from exc
        assert x >= 0
        assert x < 2**5
        return x

    if args.keep_opcodes:
        keep_opcodes = args.keep_opcodes.split(",")
        keep_opcodes = list(map(opcodes_helper, keep_opcodes))
    else:
        keep_opcodes = []
    if args.drop_opcodes:
        drop_opcodes = args.drop_opcodes.split(",")
        drop_opcodes = list(map(opcodes_helper, drop_opcodes))
    else:
        drop_opcodes = []
    if args.keep_encoding_sizes:
        keep_encoding_sizes = args.keep_encoding_sizes.split(",")
        keep_encoding_sizes = list(map(int, keep_encoding_sizes))
    else:
        keep_encoding_sizes = []
    if args.drop_encoding_sizes:
        drop_encoding_sizes = args.drop_encoding_sizes.split(",")
        drop_encoding_sizes = list(map(int, drop_encoding_sizes))
    else:
        drop_encoding_sizes = []
    # print("keep", keep_instructions)
    # print("drop", drop_instructions)
    # input("456")
    # def check_filter(name, keep, drop):
    #     if drop and keep:
    #         return name not in drop and name in keep
    #     elif keep:
    #         return name in keep
    #     elif drop:
    #         return name not in drop
    #     return True

    def check_filter_regex(name, keep, drop):
        if drop and keep:
            return not any(re.compile(expr).match(name) for expr in drop) and any(
                re.compile(expr).match(name) for expr in keep
            )
        if keep:
            return any(re.compile(expr).match(name) for expr in keep)
        if drop:
            return not any(re.compile(expr).match(name) for expr in drop)
        return True

    def check_encoding_filter(name, enc, keep, drop, keep2, drop2):
        opcode = None
        size = 0
        for e in reversed(enc):
            # print("e", e, dir(e))
            if isinstance(e, arch.BitVal):
                length = e.length
                if size == 0:
                    if length == 7:
                        val = e.value
                        opcode = val >> 2
            elif isinstance(e, arch.BitField):
                length = e.range.length
            else:
                assert False
            size += length
        assert size in [16, 32, 64, 128], f"Invalid size: {size} (Instruction: {name})"
        ret = True
        if drop2 and keep2:
            ret = size not in drop2 and size in keep2
        elif keep2:
            ret = size in keep2
        elif drop2:
            ret = size not in drop2
        if not ret:
            return False
        if opcode is None:  # not found (not a riscv insn?)
            return True
        if drop and keep:
            return opcode not in drop and opcode in keep
        if keep:
            return opcode in keep
        if drop:
            return opcode not in drop
        return True

    model_obj.sets = {
        set_name: set_def
        for set_name, set_def in model_obj.sets.items()
        if check_filter_regex(set_name, keep_sets, drop_sets)
    }
    for set_name, set_def in model_obj.sets.items():
        set_def.instructions = {
            key: instr_def
            for key, instr_def in set_def.instructions.items()
            if check_filter_regex(instr_def.name, keep_instructions, drop_instructions)
            and check_encoding_filter(
                instr_def.name, instr_def.encoding, keep_opcodes, drop_opcodes, keep_encoding_sizes, drop_encoding_sizes
            )
        }
        # for instr_name, instr_def in set_def.instructions.items():
    for set_name, set_def in model_obj.sets.items():
        set_def.extension = [
            extension
            for extension in set_def.extension
            if extension in model_obj.sets and len(model_obj.sets[extension].instructions) > 0
        ]

    # Remove sets without instructions
    model_obj.sets = {
        set_name: set_def
        for set_name, set_def in model_obj.sets.items()
        if len(set_def.instructions) > 0 or len(set_def.extension) > 0
    }

    dump_model(model_obj, out_path, compat=args.compat)


def main(argv):
    parser = get_parser()
    args = parser.parse_args(argv)
    run(args)


if __name__ == "__main__":
    main(sys.argv[1:])

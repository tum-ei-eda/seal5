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
import pickle
from typing import Union

from m2isar.metamodel import arch

logger = logging.getLogger("filter_model")


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
    return parser


def run(args):
    # initialize logging
    logging.basicConfig(level=getattr(logging, args.log.upper()))

    # resolve model paths
    top_level = pathlib.Path(args.top_level)
    # abs_top_level = top_level.resolve()

    is_seal5_model = False
    if args.output is None:  # inplace
        assert top_level.suffix in [".m2isarmodel", ".seal5model"], "Can not infer model type from file extension."
        if top_level.suffix == ".seal5model":
            is_seal5_model = True

        model_path = top_level
    else:
        model_path = pathlib.Path(args.output)
        assert top_level.suffix in [".m2isarmodel", ".seal5model"], "Can not infer model type from file extension."
        if top_level.suffix == ".seal5model":
            is_seal5_model = True

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
        OPCODE_LOOKUP = {
            "LOAD": 0b00000,
            "LOAD-FP": 0b00001,
            "custom-0": 0b00010,
            "MISC-MEM": 0b00011,
            "OP-IMM": 0b00100,
            "AUIPC": 0b00101,
            "OP-IMM-32": 0b00110,
            # "48bit": 0b00111,
            "STORE": 0b01000,
            "STORE-FP": 0b01001,
            "custom-1": 0b01010,
            "AMO": 0b01011,
            "OP": 0b01100,
            "LUI": 0b01101,
            "OP-32": 0b01110,
            # "64bit": 0b01111,
            "MADD": 0b10000,
            "MSUB": 0b10001,
            "NMADD": 0b10010,
            "NMSUB": 0b10011,
            "OP-FP": 0b10100,
            "OP-V": 0b10101,
            "custom-2": 0b10110,  # rv128i
            # "48bit2": 0b10111,
            "BRANCH": 0b11000,
            "JALR": 0b11001,
            # "reserved": 0b11010,
            "JAL": 0b11011,
            "SYSTEM": 0b11100,
            "OP-P": 0b11101,
            "custom-3": 0b11110,
            # "80bit+": 0b11111,
        }
        try:
            x = int(x, 0)
        except ValueError:
            x = OPCODE_LOOKUP.get(x, None)
            if x is None:
                raise RuntimeError(f"Opcode lookup by string failed for {x}. Options: {list(OPCODE_LOOKUP.keys())}")
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
        elif keep:
            return any(re.compile(expr).match(name) for expr in keep)
        elif drop:
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
        elif keep:
            return opcode in keep
        elif drop:
            return opcode not in drop
        return True

    model["sets"] = {
        set_name: set_def
        for set_name, set_def in model["sets"].items()
        if check_filter_regex(set_name, keep_sets, drop_sets)
    }
    for set_name, set_def in model["sets"].items():
        set_def.instructions = {
            key: instr_def
            for key, instr_def in set_def.instructions.items()
            if check_filter_regex(instr_def.name, keep_instructions, drop_instructions)
            and check_encoding_filter(
                instr_def.name, instr_def.encoding, keep_opcodes, drop_opcodes, keep_encoding_sizes, drop_encoding_sizes
            )
        }
        # for instr_name, instr_def in set_def.instructions.items():

    # Remove sets without instructions
    model["sets"] = {set_name: set_def for set_name, set_def in model["sets"].items() if len(set_def.instructions) > 0}

    logger.info("dumping model")
    with open(model_path, "wb") as f:
        if is_seal5_model:
            pickle.dump(model, f)
        else:
            if len(model["sets"]) > 0:
                assert len(model["cores"]) == 0
                pickle.dump(model["sets"], f)
            elif len(model["cores"]) > 0:
                assert len(model["sets"]) == 0
                pickle.dump(model["cores"], f)
            else:
                assert False


def main(argv):
    parser = get_parser()
    args = parser.parse_args(argv)
    run(args)


if __name__ == "__main__":
    main(sys.argv[1:])

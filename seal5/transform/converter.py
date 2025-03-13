# SPDX-License-Identifier: Apache-2.0
#
# This file is part of the M2-ISA-R project: https://github.com/tum-ei-eda/M2-ISA-R
#
# Copyright (C) 2022
# Chair of Electrical Design Automation
# Technical University of Munich

"""Tranform M2-ISA-R metamodel to Seal5 metamodel."""

import sys
import argparse
import logging
import pathlib

from m2isar.metamodel.code_info import CodeInfoBase
from m2isar.metamodel.utils.expr_preprocessor import process_attributes, process_functions, process_instructions

import seal5.model as seal5_model
from seal5.model_utils import load_model, dump_model

logger = logging.getLogger("seal5_converter")


def convert_attrs(attrs, base):
    # print("convert_attrs", attrs)
    ret = {}
    for attr, attr_val in attrs.items():
        if isinstance(attr, str):
            attr_ = base._member_map_.get(attr.upper())
            if attr_ is not None:
                ret[attr_] = attr_val
            else:
                logger.warning("Unknown attribute: %s", attr)
                ret[attr] = attr_val
        else:
            ret[attr] = attr_val
    return ret


def get_parser():
    # read command line args
    parser = argparse.ArgumentParser()
    parser.add_argument("top_level", help="A .m2isarmodel or .seal5model file.")
    parser.add_argument("--log", default="info", choices=["critical", "error", "warning", "info", "debug"])
    parser.add_argument("--prefix", default="", type=str)
    parser.add_argument("--output", "-o", type=str, default=None)
    return parser


def run(args):
    # initialize logging
    logging.basicConfig(level=getattr(logging, args.log.upper()))

    # resolve model paths
    top_level = pathlib.Path(args.top_level)

    out_path = (top_level.parent / top_level.stem) if args.output is None else args.output

    # load model
    model_obj = load_model(top_level, compat=True)
    sets = model_obj.sets
    assert len(sets) > 0, "No sets found in model"

    # preprocess model
    for set_name, set_def in sets.items():
        logger.info("preprocessing set %s", set_name)
        process_functions(set_def)
        process_instructions(set_def)
        process_attributes(set_def)

    for set_name, set_def in sets.items():
        logger.info("replacing set %s", set_name)
        for enc, instr_def in set_def.instructions.items():
            if args.prefix:
                instr_def.name = f"{args.prefix.upper()}{instr_def.name}"
                prefix_ = args.prefix.lower().replace("_", ".")
                instr_def.mnemonic = f"{prefix_}{instr_def.mnemonic}"
            set_def.instructions[enc] = seal5_model.Seal5Instruction(
                instr_def.name,
                convert_attrs(instr_def.attributes, base=seal5_model.Seal5InstrAttribute),
                instr_def.encoding,
                instr_def.mnemonic,
                instr_def.assembly,
                instr_def.operation,
                instr_def.function_info,
                [],
                {},
            )
            set_def.instructions[enc].scalars = instr_def.scalars
        for func_name, func_def in set_def.functions.items():
            func_def.attributes = convert_attrs(func_def.attributes, base=seal5_model.Seal5FunctionAttribute)
        sets[set_name] = seal5_model.Seal5InstructionSet(
            set_def.name,
            set_def.extension,
            set_def.constants,
            set_def.memories,
            set_def.functions,
            set_def.instructions,
            {},
            {},
            {},
            {},
            {},
        )

    new_model_obj = seal5_model.Seal5Model(seal5_model.SEAL5_METAMODEL_VERSION, {}, sets, CodeInfoBase.database)
    dump_model(new_model_obj, out_path)


def main(argv):
    parser = get_parser()
    args = parser.parse_args(argv)
    run(args)


if __name__ == "__main__":
    main(sys.argv[1:])

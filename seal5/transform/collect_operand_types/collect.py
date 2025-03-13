# SPDX-License-Identifier: Apache-2.0
#
# This file is part of the M2-ISA-R project: https://github.com/tum-ei-eda/M2-ISA-R
#
# Copyright (C) 2022
# Chair of Electrical Design Automation
# Technical University of Munich

"""Infer types of instruction operands from behavior."""

import sys
import argparse
import logging
import pathlib

from m2isar.metamodel import patch_model

from seal5.model_utils import load_model, dump_model

from . import visitor

logger = logging.getLogger("collect_operand_types")


class VisitorContext:
    def __init__(self, operands):
        self.operands = operands


def get_parser():
    # read command line args
    parser = argparse.ArgumentParser()
    parser.add_argument("top_level", help="A .m2isarmodel or .seal5model file.")
    parser.add_argument("--log", default="info", choices=["critical", "error", "warning", "info", "debug"])
    parser.add_argument("--output", "-o", type=str, default=None)
    parser.add_argument("--skip-failing", action="store_true")
    parser.add_argument("--compat", action="store_true")
    return parser


def run(args):
    # initialize logging
    logging.basicConfig(level=getattr(logging, args.log.upper()))

    # resolve model paths
    top_level = pathlib.Path(args.top_level)

    out_path = (top_level.parent / top_level.stem) if args.output is None else args.output

    model_obj = load_model(top_level, compat=args.compat)

    for _, set_def in model_obj.sets.items():
        logger.debug("collecting operand types for set %s", set_def.name)
        patch_model(visitor)
        for _, instr_def in set_def.instructions.items():
            context = VisitorContext(instr_def.operands)
            logger.debug("collecting operand types for instr %s", instr_def.name)
            try:
                instr_def.operation.generate(context)
            except Exception as ex:
                if args.skip_failing:
                    logger.warning("Transformation failed for instr %s", instr_def.name)
                else:
                    raise ex
            instr_def.operands = context.operands
            # print("context.raises", context.raises)
            # input("next?")

    dump_model(model_obj, out_path, compat=args.compat)


def main(argv):
    parser = get_parser()
    args = parser.parse_args(argv)
    run(args)


if __name__ == "__main__":
    main(sys.argv[1:])

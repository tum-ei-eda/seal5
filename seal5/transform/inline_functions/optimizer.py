# SPDX-License-Identifier: Apache-2.0
#
# This file is part of the M2-ISA-R project: https://github.com/tum-ei-eda/M2-ISA-R
#
# Copyright (C) 2022
# Chair of Electrical Design Automation
# Technical University of Munich

"""Inline function calls in M2-ISA-R/Seal5 metamodel."""

import sys
import argparse
import logging
import pathlib

from m2isar.metamodel import arch, patch_model

from seal5.model import Seal5FunctionAttribute
from seal5.model_utils import load_model, dump_model

from . import visitor

logger = logging.getLogger("inline_functions")


class InlineFunctionsContext:
    def __init__(self, functions: "dict[str, arch.Function]"):
        self.functions = functions


def get_parser():
    # read command line args
    parser = argparse.ArgumentParser()
    parser.add_argument("top_level", help="A .m2isarmodel or .seal5model file.")
    parser.add_argument("--log", default="info", choices=["critical", "error", "warning", "info", "debug"])
    parser.add_argument("--output", "-o", type=str, default=None)
    parser.add_argument("--compat", action="store_true")
    return parser


def run(args):
    """Main app entrypoint."""

    # initialize logging
    logging.basicConfig(level=getattr(logging, args.log.upper()))

    # resolve model paths
    top_level = pathlib.Path(args.top_level)
    # abs_top_level = top_level.resolve()

    out_path = (top_level.parent / top_level.stem) if args.output is None else args.output

    model_obj = load_model(top_level, compat=args.compat)

    for set_name, set_def in model_obj.sets.items():
        logger.debug("inline functions for set %s", set_def.name)
        patch_model(visitor)
        context = InlineFunctionsContext(set_def.functions)
        for instr_name, instr_def in set_def.instructions.items():
            logger.debug("inline_functions for instr %s", instr_def.name)
            instr_def.operation.generate(context)
        set_def.functions = {
            func_name: func_def
            for func_name, func_def in set_def.functions.items()
            if Seal5FunctionAttribute.INLINE not in func_def.attributes
        }

    dump_model(model_obj, out_path, compat=args.compat)


def main(argv):
    parser = get_parser()
    args = parser.parse_args(argv)
    run(args)


if __name__ == "__main__":
    main(sys.argv[1:])

# SPDX-License-Identifier: Apache-2.0
#
# This file is part of the M2-ISA-R project: https://github.com/tum-ei-eda/M2-ISA-R
#
# Copyright (C) 2022
# Chair of Electrical Design Automation
# Technical University of Munich

"""Clean M2-ISA-R/Seal5 metamodel by removing unused constants."""

import sys
import argparse
import logging
import pathlib

from m2isar.metamodel import patch_model

from seal5.model_utils import load_model, dump_model

from . import track_uses

logger = logging.getLogger("drop_unused")


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

    # preprocess model
    for _, set_def in model_obj.sets.items():
        logger.debug("tracking use of constants for set %s", set_def.name)
        context = DropUnusedContext(list(set_def.constants.keys()))
        patch_model(track_uses)
        for _, instr_def in set_def.instructions.items():
            logger.debug("tracking use of constants for instr %s", instr_def.name)
            instr_def.operation.generate(context)
        if len(context.to_drop) > 0:
            set_def.constants = {
                const_name: const
                for const_name, const in set_def.constants.items()
                if const_name not in context.to_drop or const_name == "XLEN"
            }
        context = DropUnusedContext(list(set_def.memories.keys()))
        for _, instr_def in set_def.instructions.items():
            logger.debug("tracking use of memories for instr %s", instr_def.name)
            instr_def.operation.generate(context)
        if len(context.to_drop) > 0:
            set_def.memories = {
                mem_name: mem for mem_name, mem in set_def.memories.items() if mem_name not in context.to_drop
            }
        context = DropUnusedContext(list(set_def.functions.keys()))
        for _, instr_def in set_def.instructions.items():
            logger.debug("tracking use of functions for instr %s", instr_def.name)
            instr_def.operation.generate(context)
        if len(context.to_drop) > 0:
            set_def.functions = {
                func_name: func for func_name, func in set_def.functions.items() if func_name not in context.to_drop
            }

    dump_model(model_obj, out_path, compat=args.compat)


def main(argv):
    parser = get_parser()
    args = parser.parse_args(argv)
    run(args)


if __name__ == "__main__":
    main(sys.argv[1:])

# SPDX-License-Identifier: Apache-2.0
#
# This file is part of the M2-ISA-R project: https://github.com/tum-ei-eda/M2-ISA-R
#
# Copyright (C) 2022
# Chair of Electrical Design Automation
# Technical University of Munich

"""Type inference for M2-ISA-R/Seal5 metamodel.

This module uses the upstream M2-ISA-R infer_types implementation which
provides the modern visitor pattern and type system.
"""

import sys
import argparse
import logging
import pathlib

from seal5.model_utils import load_model, dump_model

from .visitor import InferTypesMutator, WarningsManager
from m2isar.warnings import add_warnings_flags, KNOWN_WARNINGS

from seal5.logging import Logger

logger = Logger("transform.infer_types")


def get_parser():
    # read command line args
    parser = argparse.ArgumentParser()
    parser.add_argument("top_level", help="A .m2isarmodel or .seal5model file.")
    parser.add_argument("--log", default="info", choices=["critical", "error", "warning", "info", "debug"])
    parser.add_argument("--output", "-o", type=str, default=None)
    parser.add_argument("--compat", action="store_true")
    add_warnings_flags(parser, KNOWN_WARNINGS, KNOWN_WARNINGS)
    return parser


def run(args):
    # initialize logging
    logger.setLevel(getattr(logging, args.log.upper()))

    # resolve model paths
    top_level = pathlib.Path(args.top_level)

    out_path = (top_level.parent / top_level.stem) if args.output is None else args.output

    model_obj = load_model(top_level, compat=args.compat)

    # Build warnings info from command-line arguments
    warnings_info = args.warnings if hasattr(args, "warnings") else None

    # Process instruction sets (Seal5 specific)
    for _, set_def in model_obj.sets.items():
        logger.debug("inferring types for set %s", set_def.name)
        context = WarningsManager(warnings_info)
        mutator = InferTypesMutator()
        for _, instr_def in set_def.instructions.items():
            logger.debug("inferring types for instr %s", instr_def.name)
            mutator.generate(instr_def.operation, context)

    dump_model(model_obj, out_path, compat=args.compat)


def main(argv):
    parser = get_parser()
    args = parser.parse_args(argv)
    run(args)


if __name__ == "__main__":
    main(sys.argv[1:])

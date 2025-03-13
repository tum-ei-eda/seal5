# SPDX-License-Identifier: Apache-2.0
#
# This file is part of the M2-ISA-R project: https://github.com/tum-ei-eda/M2-ISA-R
#
# Copyright (C) 2022
# Chair of Electrical Design Automation
# Technical University of Munich

"""Optimize M2-ISA-R/Seal5 metamodel."""

import sys
import argparse
import logging
import pathlib

from m2isar.metamodel.utils.expr_preprocessor import process_instructions

from seal5.model_utils import load_model, dump_model

logger = logging.getLogger("optimizer")


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

    out_path = (top_level.parent / top_level.stem) if args.output is None else args.output

    model_obj = load_model(top_level, compat=args.compat)

    # preprocess model
    for core_name, core_def in model_obj.cores.items():
        logger.info("preprocessing core %s", core_name)
        # process_functions(core_def)
        process_instructions(core_def)
        # process_attributes(core_def)

    for set_name, set_def in model_obj.sets.items():
        logger.info("preprocessing set %s", set_name)
        # process_functions(set_def)
        process_instructions(set_def)
        # process_attributes(set_def)

    dump_model(model_obj, out_path, compat=args.compat)


def main(argv):
    parser = get_parser()
    args = parser.parse_args(argv)
    run(args)


if __name__ == "__main__":
    main(sys.argv[1:])

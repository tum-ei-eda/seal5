# SPDX-License-Identifier: Apache-2.0
#
# This file is part of the M2-ISA-R project: https://github.com/tum-ei-eda/M2-ISA-R
#
# Copyright (C) 2022
# Chair of Electrical Design Automation
# Technical University of Munich

"""Remove (rd != 0) checks from M2-ISA-R/Seal5 metamodel."""

import sys
import argparse
import logging
import pathlib

from m2isar.metamodel import patch_model

from seal5.model_utils import load_model, dump_model

from . import visitor

logger = logging.getLogger("infer_types")


# TODO: implement full API
# class TransformAPI(IntEnum):
#     PYTHON = auto()
#     CMDLINE = auto()
#
#
# class InferTypes(Seal5Transform):
#
#
#     def setup_parser(self):
#
#
#     def run(self, api: TranformAPI = TranformAPI.PYTHON):


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

    for _, set_def in model_obj.sets.items():
        logger.debug("inferring types for set %s", set_def.name)
        patch_model(visitor)
        # TODO: handle RFS symbolically
        for _, instr_def in set_def.instructions.items():
            logger.debug("inferring types for instr %s", instr_def.name)
            instr_def.operation.generate(None)

    dump_model(model_obj, out_path, compat=args.compat)


def main(argv):
    parser = get_parser()
    args = parser.parse_args(argv)
    run(args)


if __name__ == "__main__":
    main(sys.argv[1:])

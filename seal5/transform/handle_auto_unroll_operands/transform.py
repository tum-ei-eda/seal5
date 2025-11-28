# SPDX-License-Identifier: Apache-2.0
#
# This file is part of the M2-ISA-R project: https://github.com/tum-ei-eda/M2-ISA-R
#
# Copyright (C) 2022
# Chair of Electrical Design Automation
# Technical University of Munich

"""Convert auto_unroll_imm attributes."""

import sys
import argparse
import logging
import pathlib

from m2isar.metamodel import patch_model

from seal5.model_utils import load_model, dump_model
from seal5.model import Seal5InstrAttribute, Seal5OperandAttribute

from seal5.logging import Logger

logger = Logger("transform.handle_auto_unroll_operands")


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
    logger.setLevel(getattr(logging, args.log.upper()))

    # resolve model paths
    top_level = pathlib.Path(args.top_level)

    out_path = (top_level.parent / top_level.stem) if args.output is None else args.output

    model_obj = load_model(top_level, compat=args.compat)

    def handle(instr_def):
        has_auto_unroll_imm = Seal5InstrAttribute.AUTO_UNROLL_IMM in instr_def.attributes
        if not has_auto_unroll_imm:
            return
        for op_name, op_def in instr_def.operands.items():
            is_imm = Seal5OperandAttribute.IS_IMM in op_def.attributes
            if not is_imm:
                continue
            imm_ty = op_def.ty
            is_supported = imm_ty.is_int and imm_ty.is_scalar
            if not is_supported:
                continue
            imm_width = imm_ty.width
            max_imm_width = 5
            is_small_imm = imm_width <= max_imm_width
            if not is_small_imm:
                continue
            # TODO: check if immleaf?
            op_def.attributes[Seal5OperandAttribute.IS_UNROLL_IMM] = []
        pass

    for _, set_def in model_obj.sets.items():
        logger.debug("handling auto_unroll_imm attrs for set %s", set_def.name)
        for _, instr_def in set_def.instructions.items():
            logger.debug("handling auto_unroll_imm attr for instr %s", instr_def.name)
            try:
                handle(instr_def)
            except Exception as ex:
                if args.skip_failing:
                    logger.warning("Transformation failed for instr %s", instr_def.name)
                else:
                    raise ex

    dump_model(model_obj, out_path, compat=args.compat)


def main(argv):
    parser = get_parser()
    args = parser.parse_args(argv)
    run(args)


if __name__ == "__main__":
    main(sys.argv[1:])

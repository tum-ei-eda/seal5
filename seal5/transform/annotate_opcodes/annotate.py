# SPDX-License-Identifier: Apache-2.0
#
# This file is part of the M2-ISA-R project: https://github.com/tum-ei-eda/M2-ISA-R
#
# Copyright (C) 2022
# Chair of Electrical Design Automation
# Technical University of Munich

"""Annotate opcode and encoding fmt using CoreDSL2 attributes."""

import sys
import argparse
import logging
import pathlib

import pandas as pd

import seal5.model as seal5_model
from seal5.model_utils import load_model, dump_model
from seal5.riscv_utils import detect_opcode, detect_format, detect_funct3_funct7

from m2isar.metamodel import behav

logger = logging.getLogger("annotate_opcodes")


def annotate_opcodes(instr_def: seal5_model.Seal5Instruction, enc_mask: int, enc_match: int):
    enc_size = instr_def.size
    opcode_name, opcode_val = detect_opcode(instr_def)
    # print("opcode_name", opcode_name)
    # print("opcode_val", opcode_val)
    funct3_val, funct7_val = detect_funct3_funct7(instr_def)
    # print("funct3_val", funct3_val)
    # print("funct7_val", funct7_val)
    enc_format, enc_pattern = detect_format(instr_def)
    # print("enc_format", enc_format)
    # print("enc_pattern", enc_pattern)
    if opcode_val is not None:
        # TODO: IntLiteral?
        instr_def.attributes[seal5_model.Seal5InstrAttribute.OPCODE] = behav.IntLiteral(opcode_val, 7)
    if opcode_name is not None:
        instr_def.attributes[seal5_model.Seal5InstrAttribute.OPCODE_NAME] = behav.StringLiteral(opcode_name)
    if funct3_val is not None:
        instr_def.attributes[seal5_model.Seal5InstrAttribute.FUNCT3] = behav.IntLiteral(funct3_val, 3)
    if funct7_val is not None:
        instr_def.attributes[seal5_model.Seal5InstrAttribute.FUNCT7] = behav.IntLiteral(funct7_val, 7)
    if enc_format is not None:
        instr_def.attributes[seal5_model.Seal5InstrAttribute.ENC_FORMAT] = behav.StringLiteral(enc_format)
    if enc_pattern is not None:
        # TODO: StringRef?
        instr_def.attributes[seal5_model.Seal5InstrAttribute.ENC_PATTERN] = behav.StringLiteral(enc_pattern)
    if enc_mask is not None:
        instr_def.attributes[seal5_model.Seal5InstrAttribute.ENC_MASK] = behav.IntLiteral(enc_mask, enc_size)
    if enc_match is not None:
        instr_def.attributes[seal5_model.Seal5InstrAttribute.ENC_MATCH] = behav.IntLiteral(enc_match, enc_size)


def get_parser():
    # read command line args
    parser = argparse.ArgumentParser()
    parser.add_argument("top_level", help="A .m2isarmodel or .seal5model file.")
    parser.add_argument("--log", default="info", choices=["critical", "error", "warning", "info", "debug"])
    parser.add_argument("--output", "-o", type=str, default=None)
    parser.add_argument("--metrics", default=None, help="Output metrics to file")
    parser.add_argument("--compat", action="store_true")
    return parser


def run(args):
    # initialize logging
    logging.basicConfig(level=getattr(logging, args.log.upper()))

    # resolve model paths
    top_level = pathlib.Path(args.top_level)

    out_path = (top_level.parent / top_level.stem) if args.output is None else args.output

    model_obj = load_model(top_level, compat=args.compat)

    metrics = {
        "n_sets": 0,
        "n_instructions": 0,
        "n_skipped": 0,
        "n_failed": 0,
        "n_success": 0,
        "skipped_instructions": [],
        "failed_instructions": [],
        "success_instructions": [],
    }

    for set_name, set_def in model_obj.sets.items():
        metrics["n_sets"] += 1
        logger.info("processing set %s", set_name)
        for key, instr_def in set_def.instructions.items():
            metrics["n_instructions"] += 1
            logger.info("processing instruction %s", instr_def.name)
            enc_match, enc_mask = key
            # print("mask", hex(enc_mask))
            # print("match_", hex(enc_match))
            try:
                annotate_opcodes(instr_def, enc_mask, enc_match)
                metrics["n_success"] += 1
                metrics["success_instructions"].append(instr_def.name)
            except Exception as ex:
                logger.exception(ex)
                metrics["n_failed"] += 1
                metrics["failed_instructions"].append(instr_def.name)

    dump_model(model_obj, out_path, compat=args.compat)
    if args.metrics:
        metrics_file = args.metrics
        metrics_df = pd.DataFrame({key: [val] for key, val in metrics.items()})
        metrics_df.to_csv(metrics_file, index=False)


def main(argv):
    parser = get_parser()
    args = parser.parse_args(argv)
    run(args)


if __name__ == "__main__":
    main(sys.argv[1:])

# SPDX-License-Identifier: Apache-2.0
#
# This file is part of the M2-ISA-R project: https://github.com/tum-ei-eda/M2-ISA-R
#
# Copyright (C) 2022
# Chair of Electrical Design Automation
# Technical University of Munich

"""Infer types of instruction operands from behavior."""

import sys
import json
import argparse
import logging
import pathlib

import pandas as pd

from seal5.model_utils import load_model, dump_model
from seal5.register_pairs import is_pair_bank, validate_pair_bank

from .visitor import CollectRegisterOperandsVisitor
from seal5.transform.infer_register_pairs import InferRegisterPairs
from copy import deepcopy

from seal5.logging import Logger

logger = Logger("transform.collect_register_operands")


class VisitorContext:
    def __init__(self, operands, register_pairs=()):
        self.operands = operands
        self.register_pairs = set(register_pairs)
        # self.uses = None


def get_parser():
    # read command line args
    parser = argparse.ArgumentParser()
    parser.add_argument("top_level", help="A .m2isarmodel or .seal5model file.")
    parser.add_argument("--log", default="info", choices=["critical", "error", "warning", "info", "debug"])
    parser.add_argument("--output", "-o", type=str, default=None)
    parser.add_argument("--metrics", default=None, help="Output metrics to file")
    parser.add_argument("--compat", action="store_true")
    parser.add_argument("--register-pairs", type=json.loads, default={})
    return parser


def run(args):
    # initialize logging
    logger.setLevel(getattr(logging, args.log.upper()))

    # resolve model paths
    top_level = pathlib.Path(args.top_level)

    out_path = (top_level.parent / top_level.stem) if args.output is None else args.output

    # load model
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
    for _, set_def in model_obj.sets.items():
        metrics["n_sets"] += 1
        logger.debug("collecting register operands for set %s", set_def.name)
        for bank in set_def.register_banks.values():
            if is_pair_bank(bank):
                validate_pair_bank(bank, set_def.register_banks)
        visitor = CollectRegisterOperandsVisitor()
        for _, instr_def in set_def.instructions.items():
            metrics["n_instructions"] += 1
            pairs = set(args.register_pairs.get(instr_def.name, []))
            if set_def.xlen == 32:
                inference = InferRegisterPairs(instr_def.operands)
                inference.generate(deepcopy(instr_def.operation))
                pairs.update(inference.pairs)
            if pairs and set_def.xlen != 32:
                raise ValueError("Register pairs currently require RV32")
            unknown = set(pairs) - set(instr_def.operands)
            if unknown:
                raise ValueError(f"Unknown pair operands in {instr_def.name}: {unknown}")
            context = VisitorContext(instr_def.operands, pairs)
            logger.debug("collecting register operands for instr %s", instr_def.name)
            try:
                visitor.generate(instr_def.operation, context)
                instr_def.operands = context.operands
                # print("context.raises", context.raises)
                # input("next?")
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

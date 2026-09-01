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

import pandas as pd

import seal5.model
from seal5.model_utils import load_model, dump_model

from .visitor import DetectInoutsVisitor
from .utils import IOMode

from seal5.logging import Logger

logger = Logger("transform.detect_inouts")


class VisitorContext:
    def __init__(self):
        self.reads = set()
        self.writes = set()
        self.stack = []

    @property
    def uses(self):
        return self.reads | self.writes

    def push(self, mode):
        self.stack.append(mode)

    def pop(self):
        return self.stack.pop()

    @property
    def is_read(self):
        return self.stack[-1] == IOMode.READ

    @property
    def is_write(self):
        return self.stack[-1] == IOMode.WRITE


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
    logger.setLevel(getattr(logging, args.log.upper()))

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
    for _, set_def in model_obj.sets.items():
        metrics["n_sets"] += 1
        logger.debug("collecting inouts for set %s", set_def.name)
        for _, instr_def in set_def.instructions.items():
            metrics["n_instructions"] += 1
            context = VisitorContext()
            logger.debug("collecting inouts for instr %s", instr_def.name)
            try:
                DetectInoutsVisitor().generate(instr_def.operation, context)
                for op_name, op_def in instr_def.operands.items():
                    if op_name in context.reads and op_name in context.writes:
                        if seal5.model.Seal5OperandAttribute.INOUT not in instr_def.attributes:
                            op_def.attributes[seal5.model.Seal5OperandAttribute.INOUT] = []
                    elif op_name in context.reads:
                        if seal5.model.Seal5OperandAttribute.IN not in instr_def.attributes:
                            op_def.attributes[seal5.model.Seal5OperandAttribute.IN] = []
                    elif op_name in context.writes:
                        if seal5.model.Seal5OperandAttribute.OUT not in instr_def.attributes:
                            op_def.attributes[seal5.model.Seal5OperandAttribute.OUT] = []
                    if op_name not in context.uses:
                        if seal5.model.Seal5OperandAttribute.UNUSED not in instr_def.attributes:
                            op_def.attributes[seal5.model.Seal5OperandAttribute.UNUSED] = []
                reg_names = [
                    reg
                    for reg_name in list(set_def.registers.keys())
                    + list(set_def.register_banks.keys())
                    + list(set_def.register_aliases.keys())
                ]
                for reg_name in context.reads:
                    if reg_name == "PC":
                        continue
                    if reg_name in instr_def.operands.keys():
                        continue
                    if reg_name in instr_def.vars.keys():
                        continue
                    assert reg_name in reg_names
                    uses = instr_def.attributes.get(seal5.model.Seal5InstrAttribute.USES, [])
                    uses.append(reg_name)
                    instr_def.attributes[seal5.model.Seal5InstrAttribute.USES] = uses
                for reg_name in context.writes:
                    if reg_name == "PC":
                        continue
                    if reg_name in instr_def.operands.keys():
                        continue
                    if reg_name in instr_def.vars.keys():
                        continue
                    assert reg_name in reg_names
                    defs = instr_def.attributes.get(seal5.model.Seal5InstrAttribute.DEFS, [])
                    defs.append(reg_name)
                    instr_def.attributes[seal5.model.Seal5InstrAttribute.DEFS] = defs
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

# SPDX-License-Identifier: Apache-2.0
#
# This file is part of the M2-ISA-R project: https://github.com/tum-ei-eda/M2-ISA-R
#
# Copyright (C) 2022
# Chair of Electrical Design Automation
# Technical University of Munich

"""Annotate instruction which are unsupported with SKIP_PATTERN_GEN attribute."""

import sys
import argparse
import logging
import pathlib

import pandas as pd

from m2isar.metamodel import arch, behav
from seal5.model import Seal5InstrAttribute, Seal5OperandAttribute
from seal5.model_utils import load_model, dump_model


logger = logging.getLogger("check_pattern_support")


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
    for _, set_def in model_obj.sets.items():
        metrics["n_sets"] += 1
        logger.debug("checking set %s", set_def.name)
        for _, instr_def in set_def.instructions.items():
            metrics["n_instructions"] += 1
            logger.debug("checking instr %s", instr_def.name)
            try:
                attributes = instr_def.attributes

                def check_noop(operation):
                    if len(operation.statements) == 0:
                        return True
                    if len(operation.statements) == 1:
                        if isinstance(operation.statements[0], behav.Block):
                            return len(operation.statements[0].statements) == 0
                    return False

                is_noop = check_noop(instr_def.operation)
                num_ins = len(
                    [
                        op
                        for op in instr_def.operands.values()
                        if Seal5OperandAttribute.IN in op.attributes or Seal5OperandAttribute.INOUT in op.attributes
                    ]
                )
                num_outs = len(
                    [
                        op
                        for op in instr_def.operands.values()
                        if Seal5OperandAttribute.OUT in op.attributes or Seal5OperandAttribute.INOUT in op.attributes
                    ]
                )
                may_load = Seal5InstrAttribute.MAY_LOAD in attributes
                may_store = Seal5InstrAttribute.MAY_STORE in attributes
                is_rvc = instr_def.size != 32
                is_branch = arch.InstrAttribute.COND in attributes or arch.InstrAttribute.NO_CONT in attributes
                has_loop = Seal5InstrAttribute.HAS_LOOP in attributes
                # TODO: has_static_loop
                has_call = Seal5InstrAttribute.HAS_CALL in attributes
                uses_custom_reg = len(attributes.get(Seal5InstrAttribute.USES, []))
                defs_custom_reg = len(attributes.get(Seal5InstrAttribute.DEFS, []))
                # TODO: check if PC is being read/written -> not supported
                # uses_pc = ?
                skip_pattern_gen = (
                    is_noop
                    or is_rvc
                    or (num_ins == 0)
                    or (num_outs != 1)
                    or may_load
                    or may_store
                    or is_branch
                    or has_loop
                    or has_call
                    or uses_custom_reg
                    or defs_custom_reg
                )
                if skip_pattern_gen:
                    attributes[Seal5InstrAttribute.SKIP_PATTERN_GEN] = []
                # TODO: move to different/new pass (add_instr_attributes) and
                # move detections to Seal5Instr class in metamodel
                attributes[Seal5InstrAttribute.LLVM_INSTR] = behav.StringLiteral(instr_def.name)
                instr_def.attributes = attributes
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

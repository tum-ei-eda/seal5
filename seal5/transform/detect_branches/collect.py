# SPDX-License-Identifier: Apache-2.0
#
# This file is part of the M2-ISA-R project: https://github.com/tum-ei-eda/M2-ISA-R
#
# Copyright (C) 2022
# Chair of Electrical Design Automation
# Technical University of Munich

"""Identify instructions with branches and (optionally) insert branch intrinsic."""

import sys
import argparse
import logging
import pathlib

import pandas as pd

from m2isar.metamodel import patch_model
import seal5.model
from seal5.model_utils import load_model, dump_model

from . import visitor

logger = logging.getLogger("detect_branches")


class VisitorContext:
    def __init__(self, allow_branch_intrinsic: bool = False):
        self.allow_branch_intrinsic = allow_branch_intrinsic
        self.reads_pc = False
        self.writes_pc = False
        self.is_branch = False
        self.use_branch_intrinsic = False
        self.cond_stack = []
        self.found_branch = False

    @property
    def uses_pc(self):
        return self.reads_pc or self.writes_pc


def get_parser():
    # read command line args
    parser = argparse.ArgumentParser()
    parser.add_argument("top_level", help="A .m2isarmodel or .seal5model file.")
    parser.add_argument("--log", default="info", choices=["critical", "error", "warning", "info", "debug"])
    parser.add_argument("--output", "-o", type=str, default=None)
    parser.add_argument("--metrics", default=None, help="Output metrics to file")
    parser.add_argument("--compat", action="store_true")
    parser.add_argument("--insert-intrinsic", action="store_true")  # TODO: use
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
        logger.debug("collecting branches for set %s", set_def.name)
        patch_model(visitor)
        for _, instr_def in set_def.instructions.items():
            metrics["n_instructions"] += 1
            context = VisitorContext(args.insert_intrinsic)
            logger.debug("collecting branches for instr %s", instr_def.name)
            try:
                instr_def.operation.generate(context)
                # Not necessarily related to branches (see AUIPC)
                if context.uses_pc:
                    if seal5.model.Seal5InstrAttribute.USES_PC not in instr_def.attributes:
                        instr_def.attributes[seal5.model.Seal5InstrAttribute.USES_PC] = []
                if context.is_branch:
                    if seal5.model.Seal5InstrAttribute.IS_BRANCH not in instr_def.attributes:
                        instr_def.attributes[seal5.model.Seal5InstrAttribute.IS_BRANCH] = []
                if context.use_branch_intrinsic:
                    if seal5.model.Seal5InstrAttribute.USE_BRANCH_INTRINSIC not in instr_def.attributes:
                        instr_def.attributes[seal5.model.Seal5InstrAttribute.USE_BRANCH_INTRINSIC] = []
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

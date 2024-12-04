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
import pickle
from typing import Union

import pandas as pd

from m2isar.metamodel import arch, behav
import seal5.model
from seal5.model import Seal5InstrAttribute, Seal5OperandAttribute


logger = logging.getLogger("check_pattern_support")


def get_parser():
    # read command line args
    parser = argparse.ArgumentParser()
    parser.add_argument("top_level", help="A .m2isarmodel or .seal5model file.")
    parser.add_argument("--log", default="info", choices=["critical", "error", "warning", "info", "debug"])
    parser.add_argument("--output", "-o", type=str, default=None)
    parser.add_argument("--metrics", default=None, help="Output metrics to file")
    return parser


def run(args):
    # initialize logging
    logging.basicConfig(level=getattr(logging, args.log.upper()))

    # resolve model paths
    top_level = pathlib.Path(args.top_level)

    is_seal5_model = False
    if args.output is None:  # inplace
        assert top_level.suffix in [".m2isarmodel", ".seal5model"], "Can not infer model type from file extension."
        if top_level.suffix == ".seal5model":
            is_seal5_model = True

        model_path = top_level
    else:
        model_path = pathlib.Path(args.output)

    logger.info("loading models")
    if not is_seal5_model:
        raise NotImplementedError

    # load models
    with open(top_level, "rb") as f:
        # models: "dict[str, arch.CoreDef]" = pickle.load(f)
        if is_seal5_model:
            model: "dict[str, Union[arch.InstructionSet, ...]]" = pickle.load(f)
            model["cores"] = {}
        else:  # TODO: core vs. set!
            temp: "dict[str, Union[arch.InstructionSet, arch.CoreDef]]" = pickle.load(f)
            assert len(temp) > 0, "Empty model!"
            if isinstance(list(temp.values())[0], arch.CoreDef):
                model = {"cores": temp, "sets": {}}
            elif isinstance(list(temp.values())[0], arch.InstructionSet):
                model = {"sets": temp, "cores": {}}
            else:
                assert False

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
    for _, set_def in model["sets"].items():
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
                has_loop = arch.InstrAttribute.HAS_LOOP in attributes
                # TODO: has_static_loop
                has_call = arch.InstrAttribute.HAS_CALL in attributes
                uses_custom_reg = len(attributes.get(Seal5InstrAttribute.USES, []))
                defs_custom_reg = len(attributes.get(Seal5InstrAttribute.DEFS, []))
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
                # TODO: move to different/new pass (add_instr_attributes) and move detections to Seal5Instr class in metamodel
                attributes[Seal5InstrAttribute.LLVM_INSTR] = behav.StringLiteral(instr_def.name)
                instr_def.attributes = attributes
                metrics["n_success"] += 1
                metrics["success_instructions"].append(instr_def.name)
            except Exception as ex:
                logger.exception(ex)
                metrics["n_failed"] += 1
                metrics["failed_instructions"].append(instr_def.name)

    logger.info("dumping model")
    with open(model_path, "wb") as f:
        if is_seal5_model:
            pickle.dump(model, f)
        else:
            if len(model["sets"]) > 0:
                assert len(model["cores"]) == 0
                pickle.dump(model["sets"], f)
            elif len(model["cores"]) > 0:
                assert len(model["sets"]) == 0
                pickle.dump(model["cores"], f)
            else:
                assert False
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

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
import pickle
from typing import Union

import pandas as pd

from m2isar.metamodel import arch, patch_model
import seal5.model

from . import visitor

logger = logging.getLogger("detect_side_effects")


class VisitorContext:
    def __init__(self):
        self.is_read = False
        self.is_write = False
        self.may_load = False
        self.may_store = False
        self.is_branch = False  # TODO
        self.is_terminator = False  # TODO
        self.is_barrier = False  # TODO
        self.is_return = False  # TODO
        self.is_call = False  # TODO
        self.is_re_materializable = False
        self.is_as_cheap_as_a_move = False


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
        logger.debug("collecting side effects for set %s", set_def.name)
        patch_model(visitor)
        for _, instr_def in set_def.instructions.items():
            metrics["n_instructions"] += 1
            context = VisitorContext()
            logger.debug("collecting side effects for instr %s", instr_def.name)
            try:
                instr_def.operation.generate(context)
                # TODO:
                # if arch.InstrAttribute.NO_CONT:
                # if arch.InstrAttribute.COND:
                if context.may_load:
                    if seal5.model.Seal5InstrAttribute.MAY_LOAD not in instr_def.attributes:
                        instr_def.attributes[seal5.model.Seal5InstrAttribute.MAY_LOAD] = []
                if context.may_store:
                    if seal5.model.Seal5InstrAttribute.MAY_STORE not in instr_def.attributes:
                        instr_def.attributes[seal5.model.Seal5InstrAttribute.MAY_STORE] = []
                # TODO
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

# SPDX-License-Identifier: Apache-2.0
#
# This file is part of the seal5 project: https://github.com/tum-ei-eda/seal5
#
# Copyright (C) 2024
# Chair of Electrical Design Automation
# Technical University of Munich

"""TODO."""

import sys
import argparse
import logging
import pathlib
import pickle
from typing import Union

from m2isar.metamodel import arch, patch_model
import seal5.model

from . import dag_builder
from .context import DAGBuilderContext

logger = logging.getLogger("detect_branches")


def get_parser():
    # read command line args
    parser = argparse.ArgumentParser()
    parser.add_argument("top_level", help="A .m2isarmodel or .seal5model file.")
    parser.add_argument("--log", default="info", choices=["critical", "error", "warning", "info", "debug"])
    parser.add_argument("--output", "-o", type=str, default=None)
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

    patch_model(dag_builder)
    for set_name, set_def in model["sets"].items():
        logger.debug("collecting side effects for set %s", set_def.name)
        for _, instr_def in set_def.instructions.items():
            print("instr_def", instr_def)
            context = DAGBuilderContext()
            instr_def.operation.generate(context)
            patterns = context.patterns
            print("patterns", patterns)
            complex_patterns = context.complex_patterns
            print("complex_patterns", complex_patterns)
            input(">>>")

            context = VisitorContext()
            logger.debug("collecting side effects for instr %s", instr_def.name)
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


def main(argv):
    parser = get_parser()
    args = parser.parse_args(argv)
    run(args)


if __name__ == "__main__":
    main(sys.argv[1:])

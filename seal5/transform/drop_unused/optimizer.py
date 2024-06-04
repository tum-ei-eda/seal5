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

from . import track_uses
from m2isar.metamodel import arch, patch_model

logger = logging.getLogger("drop_unused")


class DropUnusedContext:
    def __init__(self, names: "list[str]"):
        self.names = names
        self.to_keep = set()

    @property
    def to_drop(self):
        return set(name for name in self.names if name not in self.to_keep)

    def track(self, name: str):
        if name in self.names:
            # logger.debug("Tracked use of %s", name)
            self.to_keep.add(name)


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
    # abs_top_level = top_level.resolve()

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

    # preprocess model
    # print("model", model["sets"]["XCoreVMac"].keys())
    for set_name, set_def in model["sets"].items():
        logger.debug("tracking use of constants for set %s", set_def.name)
        context = DropUnusedContext(list(set_def.constants.keys()))
        patch_model(track_uses)
        for instr_name, instr_def in set_def.instructions.items():
            logger.debug("tracking use of constants for instr %s", instr_def.name)
            instr_def.operation.generate(context)
        # print("context.to_keep", context.to_keep)
        # print("context.to_drop", context.to_drop)
        if len(context.to_drop) > 0:
            # print("BEFORE", len(set_def.constants))
            set_def.constants = {
                const_name: const
                for const_name, const in set_def.constants.items()
                if const_name not in context.to_drop
            }
            # print("AFTER", len(set_def.constants))
        # input("CONT1")
        context = DropUnusedContext(list(set_def.memories.keys()))
        for instr_name, instr_def in set_def.instructions.items():
            logger.debug("tracking use of memories for instr %s", instr_def.name)
            instr_def.operation.generate(context)
        # print("context.to_keep", context.to_keep)
        # print("context.to_drop", context.to_drop)
        if len(context.to_drop) > 0:
            # print("BEFORE", len(set_def.memories))
            set_def.memories = {
                mem_name: mem for mem_name, mem in set_def.memories.items() if mem_name not in context.to_drop
            }
            # print("AFTER", len(set_def.memories))
        # input("CONT1")
        context = DropUnusedContext(list(set_def.functions.keys()))
        for instr_name, instr_def in set_def.instructions.items():
            logger.debug("tracking use of functions for instr %s", instr_def.name)
            instr_def.operation.generate(context)
        # print("context.to_keep", context.to_keep)
        # print("context.to_drop", context.to_drop)
        if len(context.to_drop) > 0:
            # print("BEFORE", len(set_def.memories))
            set_def.functions = {
                func_name: func for func_name, func in set_def.functions.items() if func_name not in context.to_drop
            }
            # print("AFTER", len(set_def.memories))
        # input("CONT1")

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

# SPDX-License-Identifier: Apache-2.0
#
# This file is part of the M2-ISA-R project: https://github.com/tum-ei-eda/M2-ISA-R
#
# Copyright (C) 2022
# Chair of Electrical Design Automation
# Technical University of Munich

"""Filter M2-ISA-R/Seal5 metamodel."""

import argparse
import logging
import pathlib
import pickle
from collections import defaultdict

from m2isar.metamodel import arch, patch_model
from m2isar.metamodel.utils.expr_preprocessor import process_attributes, process_functions, process_instructions

logger = logging.getLogger("filter_model")


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


def main():
    """Main app entrypoint."""

    # read command line args
    parser = argparse.ArgumentParser()
    parser.add_argument("top_level", help="A .m2isarmodel or .seal5model file.")
    parser.add_argument("--keep-sets", type=str, default=None)
    parser.add_argument("--drop-sets", type=str, default=None)
    parser.add_argument("--keep-instructions", type=str, default=None)
    parser.add_argument("--drop-instructions", type=str, default=None)
    # TODO: filter builtins/aliases
    parser.add_argument("--log", default="info", choices=["critical", "error", "warning", "info", "debug"])
    parser.add_argument("--output", "-o", type=str, default=None)
    args = parser.parse_args()

    # initialize logging
    logging.basicConfig(level=getattr(logging, args.log.upper()))

    # resolve model paths
    top_level = pathlib.Path(args.top_level)
    abs_top_level = top_level.resolve()

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
            temp: "dict[str, Union[arch.InstructionSet, arch.CoreDef]" = pickle.load(f)
            assert len(temp) > 0, "Empty model!"
            if isinstance(list(temp.values())[0], arch.CoreDef):
                model = {"cores": temp, "sets": {}}
            elif isinstance(list(temp.values())[0], arch.InstructionSet):
                model = {"sets": temp, "cores": {}}
            else:
                assert False

    # preprocess model
    # print("model", model["sets"]["XCoreVMac"].keys())
    if args.keep_sets:
        keep_sets = args.keep_sets.split(",")
    else:
        keep_sets = []
    if args.drop_sets:
        drop_sets = args.drop_sets.split(",")
    if args.keep_instructions:
        keep_instructions = args.keep_instructions.split(",")
    else:
        keep_instructions = []
    if args.drop_instructions:
        drop_instructions = args.drop_instructions.split(",")
    else:
        drop_instructions = []

    def check_filter(name, keep, drop):
        if drop and keep:
            return name not in drop or name in keep
        elif keep:
            return name in keep
        elif drop:
            return name not in drop
        return True

    model["sets"] = {
        set_name: set_def for set_name, set_def in model["sets"].items() if check_filter(set_name, keep_sets, drop_sets)
    }
    for set_name, set_def in model["sets"].items():
        set_def.instructions = {
            instr_name: instr_def
            for instr_name, instr_def in set_def.instructions.items()
            if check_filter(instr_name, keep_instructions, drop_instructions)
        }
        # for instr_name, instr_def in set_def.instructions.items():

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


if __name__ == "__main__":
    main()

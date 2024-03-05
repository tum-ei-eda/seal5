# SPDX-License-Identifier: Apache-2.0
#
# This file is part of the M2-ISA-R project: https://github.com/tum-ei-eda/M2-ISA-R
#
# Copyright (C) 2022
# Chair of Electrical Design Automation
# Technical University of Munich

"""Clean M2-ISA-R/Seal5 metamodel to .core_desc file."""

import argparse
import logging
import pathlib
import pickle
from typing import Union

import yaml

from m2isar.metamodel import arch

logger = logging.getLogger("yaml_writer")

# @dataclass
# class Seal5Settings(YAMLSettings):
#     extensions: Optional[Dict[str, ExtensionsSettings]] = None
# @dataclass
# class ExtensionsSettings(YAMLSettings):
#     feature: Optional[str] = None
#     arch: Optional[str] = None
#     version: Optional[str] = None
#     experimental: Optional[bool] = None
#     vendor: Optional[bool] = None
#     instructions: Optional[List[str]] = None
#     NEW: model
#     # patches


def main():
    """Main app entrypoint."""

    # read command line args
    parser = argparse.ArgumentParser()
    parser.add_argument("top_level", help="A .m2isarmodel or .seal5model file.")
    parser.add_argument("--log", default="info", choices=["critical", "error", "warning", "info", "debug"])
    parser.add_argument("--output", "-o", type=str, default=None)
    args = parser.parse_args()

    # initialize logging
    logging.basicConfig(level=getattr(logging, args.log.upper()))

    # resolve model paths
    top_level = pathlib.Path(args.top_level)
    # abs_top_level = top_level.resolve()

    is_seal5_model = False
    # print("top_level", top_level)
    # print("suffix", top_level.suffix)
    if top_level.suffix == ".seal5model":
        is_seal5_model = True
    if args.output is None:
        assert top_level.suffix in [".m2isarmodel", ".seal5model"], "Can not infer model type from file extension."

        out_path = top_level.parent / (top_level.stem + ".core_desc")
    else:
        out_path = pathlib.Path(args.output)

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
    # print("model", model)
    data = {"extensions": {}}
    for set_name, set_def in model["sets"].items():
        # print("set", set_def)
        set_data = {"instructions": []}
        set_data["model"] = top_level.stem
        for instr in set_def.instructions.values():
            set_data["instructions"].append(instr.name)
        data["extensions"][set_name] = set_data
    with open(out_path, "w") as f:
        yaml.dump(data, f)


if __name__ == "__main__":
    main()

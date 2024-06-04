# SPDX-License-Identifier: Apache-2.0
#
# This file is part of the M2-ISA-R project: https://github.com/tum-ei-eda/M2-ISA-R
#
# Copyright (C) 2022
# Chair of Electrical Design Automation
# Technical University of Munich

"""Remove (rd != 0) checks from M2-ISA-R/Seal5 metamodel."""

import sys
import argparse
import logging
import pathlib
import pickle
from typing import Union

from m2isar.metamodel import arch

from seal5.settings import Seal5Settings, ExtensionsSettings

logger = logging.getLogger("process_settings")


def get_parser():
    # read command line args
    parser = argparse.ArgumentParser()
    parser.add_argument("top_level", help="A .m2isarmodel or .seal5model file.")
    parser.add_argument("--log", default="info", choices=["critical", "error", "warning", "info", "debug"])
    parser.add_argument("--output", "-o", type=str, default=None)
    parser.add_argument("--yaml", type=str, default=None)
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

    # load settings
    if args.yaml is None:
        raise RuntimeError("Undefined --yaml not allowed")
    settings = Seal5Settings.from_yaml_file(args.yaml)

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

    assert "settings" not in model
    model["settings"] = settings

    for set_name, set_def in model["sets"].items():
        ext_settings = settings.extensions.get(set_name, None)
        if ext_settings is None:
            # Fallback!
            ext_settings = ExtensionsSettings(feature=set_name.replace("_", ""))
            # TODOL extract other details from attributes
        assert set_def.settings is None
        set_def.settings = ext_settings  # TODO: decide how to do this properly

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

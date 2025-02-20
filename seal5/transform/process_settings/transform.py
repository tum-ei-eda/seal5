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

from seal5.settings import Seal5Settings, ExtensionsSettings, RISCVSettings
from seal5.model_utils import load_model, dump_model

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

    out_path = (top_level.parent / top_level.stem) if args.output is None else args.output
    model_name = top_level.stem

    model_obj = load_model(top_level, compat=False)

    # load settings
    if args.yaml is None:
        raise RuntimeError("Undefined --yaml not allowed")
    settings = Seal5Settings.from_yaml_file(args.yaml)

    if model_obj.settings is None:
        model_obj.settings = settings
    else:
        model_obj.settings.merge(settings, overwrite=True, inplace=True)

    for set_name, set_def in model_obj.sets.items():
        model_settings = settings.models.get(model_name)
        ext_settings = None
        if model_settings is not None:
            ext_settings = model_settings.extensions.get(set_name, None)
        if ext_settings is None:
            ext_settings = ExtensionsSettings(feature=set_name.replace("_", ""))
        riscv_settings = ext_settings.riscv
        if riscv_settings is None:
            riscv_settings = RISCVSettings(xlen=set_def.xlen)
        if riscv_settings.xlen is None:
            riscv_settings.xlen = set_def.xlen
        if set_def.settings is None:
            set_def.settings = ext_settings  # TODO: decide how to do this properly
        else:
            set_def.settings.merge(ext_settings, overwrite=True, inplace=True)

    dump_model(model_obj, out_path)


def main(argv):
    parser = get_parser()
    args = parser.parse_args(argv)
    run(args)


if __name__ == "__main__":
    main(sys.argv[1:])

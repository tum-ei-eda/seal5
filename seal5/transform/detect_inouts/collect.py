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

from m2isar.metamodel import arch, patch_model
import seal5.model

from . import visitor

logger = logging.getLogger("detect_inouts")


class VisitorContext:
    def __init__(self):
        self.reads = set()
        self.writes = set()
        self.is_read = False
        self.is_write = False


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

    for _, set_def in model["sets"].items():
        logger.debug("collecting inouts for set %s", set_def.name)
        patch_model(visitor)
        for _, instr_def in set_def.instructions.items():
            context = VisitorContext()
            logger.debug("collecting inouts for instr %s", instr_def.name)
            instr_def.operation.generate(context)
            for op_name, op_def in instr_def.operands.items():
                if op_name in context.reads and op_name in context.writes:
                    if seal5.model.Seal5OperandAttribute.INOUT not in instr_def.attributes:
                        op_def.attributes[seal5.model.Seal5OperandAttribute.INOUT] = []
                elif op_name in context.reads:
                    if seal5.model.Seal5OperandAttribute.IN not in instr_def.attributes:
                        op_def.attributes[seal5.model.Seal5OperandAttribute.IN] = []
                elif op_name in context.writes:
                    if seal5.model.Seal5OperandAttribute.OUT not in instr_def.attributes:
                        op_def.attributes[seal5.model.Seal5OperandAttribute.OUT] = []
            # print("---")
            # print("instr_def.scalars.keys()", instr_def.scalars.keys())
            for reg_name in context.reads:
                # print("reg_name1", reg_name)
                if reg_name in instr_def.operands.keys():
                    continue
                if reg_name in instr_def.scalars.keys():
                    continue
                # TODO: how about register groups
                # TODO: handle other architectural state vars here (PC,...)
                assert reg_name in set_def.registers
                uses = instr_def.attributes.get(seal5.model.Seal5InstrAttribute.USES, [])
                uses.append(reg_name)
                # TODO: drop duplicates?
                instr_def.attributes[seal5.model.Seal5InstrAttribute.USES] = uses
            for reg_name in context.writes:
                # print("reg_name2", reg_name)
                if reg_name in instr_def.operands.keys():
                    continue
                if reg_name in instr_def.scalars.keys():
                    continue
                # TODO: how about register groups
                # TODO: handle other architectural state vars here (PC,...)
                assert reg_name in set_def.registers
                defs = instr_def.attributes.get(seal5.model.Seal5InstrAttribute.DEFS, [])
                defs.append(reg_name)
                # TODO: drop duplicates?
                instr_def.attributes[seal5.model.Seal5InstrAttribute.DEFS] = defs
            # print("instr_def.operands_", instr_def.operands)
            # print("instr_def.attributes", instr_def.attributes)
            # input("999")

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

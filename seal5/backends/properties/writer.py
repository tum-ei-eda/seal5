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

import pandas as pd

from m2isar.metamodel import arch
from seal5.model import Seal5OperandAttribute, Seal5InstrAttribute

logger = logging.getLogger("properties_writer")


def main():
    """Main app entrypoint."""

    # read command line args
    parser = argparse.ArgumentParser()
    parser.add_argument("top_level", help="A .m2isarmodel or .seal5model file.")
    parser.add_argument("--log", default="info", choices=["critical", "error", "warning", "info", "debug"])
    parser.add_argument("--output", "-o", type=str, default=None)
    parser.add_argument("--fmt", type=str, choices=["auto", "csv", "pkl", "md"], default="auto")
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
    assert args.output is not None
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
    properties_data = []
    for set_name, set_def in model["sets"].items():
        # print("set_name", set_name)
        xlen = set_def.xlen
        model = top_level.stem

        def get_set_properties(set_name, xlen):
            is_rv32 = xlen == 32
            is_rv64 = xlen == 64
            return {
                "set": set_name,
                "xlen": xlen,
                "is_rv32": is_rv32,
                "is_rv64": is_rv64,
            }

        for instr_def in set_def.instructions.values():
            instr_name = instr_def.name
            # print("instr_name", instr_name)
            operands = instr_def.operands

            def get_operands_properties(operands):
                num_operands = len(operands)
                num_inputs = len([op for op in operands.values() if Seal5OperandAttribute.IN in op.attributes])
                num_outputs = len([op for op in operands.values() if Seal5OperandAttribute.OUT in op.attributes])
                num_inouts = len([op for op in operands.values() if Seal5OperandAttribute.INOUT in op.attributes])
                num_regs = len([op for op in operands.values() if Seal5OperandAttribute.IS_REG in op.attributes])
                num_gprs = len(
                    [
                        op
                        for op in operands.values()
                        if Seal5OperandAttribute.IS_REG in op.attributes
                        and op.attributes[Seal5OperandAttribute.REG_CLASS] == "GPR"
                    ]
                )
                num_imms = len([op for op in operands.values() if Seal5OperandAttribute.IS_IMM in op.attributes])
                imm_types = set(
                    op.attributes[Seal5OperandAttribute.IS_REG]
                    for op in operands.values()
                    if Seal5OperandAttribute.IS_IMM in op.attributes
                )
                is_multi_in = num_inputs + num_inouts > 1
                is_single_in = num_inputs + num_inouts == 1
                is_multi_out = num_outputs + num_inouts > 1
                is_single_out = num_outputs + num_inouts == 1
                is_mimo = is_multi_in and is_multi_out
                is_miso = is_multi_in and is_single_out
                is_siso = is_single_in and is_single_out
                is_simo = is_single_in and is_multi_out
                return {
                    "num_operands": num_operands,
                    "num_inputs": num_inputs,
                    "num_outputs": num_outputs,
                    "num_inouts": num_inouts,
                    "num_regs": num_regs,
                    "num_gprs": num_gprs,
                    "num_imms": num_imms,
                    "imm_types": imm_types,
                    "is_multi_in": is_multi_in,
                    "is_single_in": is_single_in,
                    "is_multi_out": is_multi_out,
                    "is_single_out": is_single_out,
                    "is_mimo": is_mimo,
                    "is_miso": is_miso,
                    "is_siso": is_siso,
                    "is_simo": is_simo,
                    # TODO: num_csrs, num_fprs, num_custom...
                }

            def get_side_effect_properties(attrs):
                uses_custom_reg = Seal5InstrAttribute.USES in attrs and len(attrs[Seal5InstrAttribute.USES]) > 0
                defs_custom_reg = Seal5InstrAttribute.DEFS in attrs and len(attrs[Seal5InstrAttribute.DEFS]) > 0
                return {
                    "has_side_effects": Seal5InstrAttribute.HAS_SIDE_EFFECTS in attrs,
                    "may_load": Seal5InstrAttribute.MAY_LOAD in attrs,
                    "may_store": Seal5InstrAttribute.MAY_STORE in attrs,
                    "is_terminator": Seal5InstrAttribute.IS_TERMINATOR in attrs,
                    "is_branch": Seal5InstrAttribute.IS_BRANCH in attrs,
                    "uses_custom_reg": uses_custom_reg,
                    "defs_custom_reg": defs_custom_reg,
                }

            attrs = instr_def.attributes
            data = {
                "model": model,
                **get_set_properties(set_name, xlen),
                "instr": instr_name,
                **get_operands_properties(operands),
                **get_side_effect_properties(attrs),
                # TODO: operations
            }
            properties_data.append(data)
    properties_df = pd.DataFrame(properties_data)
    fmt = args.fmt
    if fmt == "auto":
        fmt = out_path.suffix
        assert len(fmt) > 1
        fmt = fmt[1:].lower()

    if fmt == "csv":
        properties_df.to_csv(out_path, index=False)
    elif fmt == "pkl":
        properties_df.to_pickle(out_path)
    elif fmt == "md":
        # properties_df.to_markdown(out_path, tablefmt="grid", index=False)
        properties_df.to_markdown(out_path, index=False)
    else:
        raise ValueError(f"Unsupported fmt: {fmt}")


if __name__ == "__main__":
    main()

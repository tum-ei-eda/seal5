# SPDX-License-Identifier: Apache-2.0
#
# This file is part of the M2-ISA-R project: https://github.com/tum-ei-eda/M2-ISA-R
#
# Copyright (C) 2022
# Chair of Electrical Design Automation
# Technical University of Munich

"""Properties report writer for Seal5."""

import argparse
import logging
import pathlib

import pandas as pd

from seal5.model import Seal5OperandAttribute, Seal5InstrAttribute
from seal5.model_utils import load_model
from seal5.riscv_utils import detect_opcode, detect_format

from seal5.logging import Logger

logger = Logger("backends.properties_writer")


def main():
    """Main app entrypoint."""

    # read command line args
    parser = argparse.ArgumentParser()
    parser.add_argument("top_level", nargs="+", help="A .m2isarmodel or .seal5model file.")
    parser.add_argument("--log", default="info", choices=["critical", "error", "warning", "info", "debug"])
    parser.add_argument("--output", "-o", type=str, default=None)
    parser.add_argument("--fmt", type=str, choices=["auto", "csv", "pkl", "md"], default="auto")
    parser.add_argument("--compat", action="store_true")
    args = parser.parse_args()

    # initialize logging
    logger.setLevel(getattr(logging, args.log.upper()))

    assert args.output is not None
    out_path = pathlib.Path(args.output)

    # resolve model paths
    properties_data = []
    top_levels = args.top_level
    for top_level in top_levels:
        top_level = pathlib.Path(top_level)

        model_obj = load_model(top_level, compat=args.compat)

        # preprocess model
        # print("model", model)
        for set_name, set_def in model_obj.sets.items():
            # print("set_name", set_name)
            if len(set_def.instructions) == 0:
                continue
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

                def get_enc_properties(instr_def):
                    enc_size = instr_def.size
                    is_compressed = enc_size == 16
                    # TODO: opcode
                    # TODO: format

                    # opcode, _ = detect_opcode(instr_def)
                    # enc_format, _ = detect_format(instr_def)
                    opcode = instr_def.attributes.get(Seal5InstrAttribute.OPCODE_NAME)
                    if opcode is None:
                        opcode, _ = detect_opcode(instr_def)
                    else:
                        opcode = opcode.value
                    enc_format = instr_def.attributes.get(Seal5InstrAttribute.ENC_FORMAT)
                    if enc_format is None:
                        enc_format, _ = detect_format(instr_def)
                    else:
                        enc_format = enc_format.value

                    return {
                        "enc_size": enc_size,
                        "is_compressed": is_compressed,
                        "enc_format": enc_format,
                        "opcode": opcode,
                    }

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
                        op.attributes[Seal5OperandAttribute.TYPE]
                        for op in operands.values()
                        if Seal5OperandAttribute.IS_IMM in op.attributes
                    )
                    has_imm_leaf = any(
                        Seal5OperandAttribute.IS_IMM_LEAF in op.attributes
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
                        "has_imm_leaf": has_imm_leaf,
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
                        "skip_pattern_gen": Seal5InstrAttribute.SKIP_PATTERN_GEN in attrs,
                        "uses_custom_reg": uses_custom_reg,
                        "defs_custom_reg": defs_custom_reg,
                    }

                attrs = instr_def.attributes
                data = {
                    "model": model,
                    **get_set_properties(set_name, xlen),
                    "instr": instr_name,
                    **get_enc_properties(instr_def),
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

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
    parser.add_argument("top_level", nargs="+", help="A .m2isarmodel or .seal5model file.")
    parser.add_argument("--log", default="info", choices=["critical", "error", "warning", "info", "debug"])
    parser.add_argument("--output", "-o", type=str, default=None)
    parser.add_argument("--fmt", type=str, choices=["auto", "csv", "pkl", "md"], default="auto")
    args = parser.parse_args()

    # initialize logging
    logging.basicConfig(level=getattr(logging, args.log.upper()))

    assert args.output is not None
    out_path = pathlib.Path(args.output)

    # resolve model paths
    properties_data = []
    top_levels = args.top_level
    for top_level in top_levels:
        top_level = pathlib.Path(top_level)

        is_seal5_model = False
        # print("top_level", top_level)
        # print("suffix", top_level.suffix)
        if top_level.suffix == ".seal5model":
            is_seal5_model = True
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


                    def get_enc_properties(instr_def):
                        enc_size = instr_def.size
                        is_compressed = enc_size == 16
                        # TODO: opcode
                        # TODO: format

                        def detect_opcode(instr_def):  # TODO: move to transform and store as attr
                            OPCODE_LOOKUP = {
                                "LOAD": 0b00000,
                                "LOAD-FP": 0b00001,
                                "custom-0": 0b00010,
                                "MISC-MEM": 0b00011,
                                "OP-IMM": 0b00100,
                                "AUIPC": 0b00101,
                                "OP-IMM-32": 0b00110,
                                # "48bit": 0b00111,
                                "STORE": 0b01000,
                                "STORE-FP": 0b01001,
                                "custom-1": 0b01010,
                                "AMO": 0b01011,
                                "OP": 0b01100,
                                "LUI": 0b01101,
                                "OP-32": 0b01110,
                                # "64bit": 0b01111,
                                "MADD": 0b10000,
                                "MSUB": 0b10001,
                                "NMADD": 0b10010,
                                "NMSUB": 0b10011,
                                "OP-FP": 0b10100,
                                "OP-V": 0b10101,
                                "custom-2": 0b10110,  # rv128i
                                # "48bit2": 0b10111,
                                "BRANCH": 0b11000,
                                "JALR": 0b11001,
                                # "reserved": 0b11010,
                                "JAL": 0b11011,
                                "SYSTEM": 0b11100,
                                "OP-P": 0b11101,
                                "custom-3": 0b11110,
                                # "80bit+": 0b11111,
                            }
                            OPCODE_LOOKUP_REV = {v: k for k, v in OPCODE_LOOKUP.items()}
                            size = 0  # TODO: use instr_def.size
                            for e in reversed(instr_def.encoding):
                                # print("e", e, dir(e))
                                if isinstance(e, arch.BitVal):
                                    length = e.length
                                    if size == 0:
                                        if length == 7:
                                            val = e.value
                                            opcode = val >> 2
                                elif isinstance(e, arch.BitField):
                                    length = e.range.length
                                else:
                                    assert False
                                size += length
                            if size != 32:  # TODO: support compressed opcodes
                                assert size == 16
                                return "COMPRESSED"
                            assert opcode is not None
                            found = OPCODE_LOOKUP_REV.get(opcode, None)
                            assert found is not None, f"Opcode not found: {bin(opcode)}"
                            return found

                        def detect_format(instr_def):  # TODO: move to transform and store as attr
                            return "unknown"

                        opcode = detect_opcode(instr_def)
                        enc_format = detect_format(instr_def)

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

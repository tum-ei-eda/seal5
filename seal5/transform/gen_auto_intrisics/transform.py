# SPDX-License-Identifier: Apache-2.0
#
# This file is part of the M2-ISA-R project: https://github.com/tum-ei-eda/M2-ISA-R
#
# Copyright (C) 2022
# Chair of Electrical Design Automation
# Technical University of Munich

"""Generate missing intrinsics definitions automatically."""

import sys
import argparse
import logging
import pathlib

from seal5.model_utils import load_model, dump_model
from seal5.model import Seal5InstrAttribute, Seal5OperandAttribute
from seal5.settings import IntrinsicArg, IntrinsicDefn
from m2isar.metamodel import arch

from seal5.logging import Logger

logger = Logger("transform.process_settings")


# TODO: move to utils
def next_power_of_two_ge_8(n):
    MIN_POW2 = 8
    if n >= MIN_POW2 and (n & (n - 1)) == 0:
        return n
    next_pow2 = 1 << (n - 1).bit_length()
    return max(next_pow2, MIN_POW2)


def get_parser():
    # read command line args
    parser = argparse.ArgumentParser()
    parser.add_argument("top_level", help="A .m2isarmodel or .seal5model file.")
    parser.add_argument("--log", default="info", choices=["critical", "error", "warning", "info", "debug"])
    parser.add_argument("--output", "-o", type=str, default=None)
    parser.add_argument("--skip-failing", action="store_true")
    # parser.add_argument("--yaml", type=str, default=None)
    return parser


def run(args):
    # initialize logging
    logger.setLevel(getattr(logging, args.log.upper()))

    # resolve model paths
    top_level = pathlib.Path(args.top_level)

    out_path = (top_level.parent / top_level.stem) if args.output is None else args.output
    # model_name = top_level.stem

    model_obj = load_model(top_level, compat=False)

    # load settings
    # if args.yaml is None:
    #     raise RuntimeError("Undefined --yaml not allowed")
    # settings = Seal5Settings.from_yaml_file(args.yaml)

    assert model_obj.settings is not None
    settings = model_obj.settings
    instrinsics_settings = settings.intrinsics
    print("instrinsics_settings", instrinsics_settings)

    def handle(instr_def, intrinsics_settings, set_name):
        has_auto_intrin = Seal5InstrAttribute.AUTO_INTRIN in instr_def.attributes
        if not has_auto_intrin:
            return
        intrinsics = intrinsics_settings.intrinsics
        if intrinsics is None:
            intrinsics = []
        # print("handle")
        # print("instr_def", instr_def)
        instr_name = instr_def.name
        # print("instr_name", instr_name)
        has_intrinsic = any(
            intrin.set_name.lower() == set_name.lower() and intrin.instr_name.lower() == instr_name.lower()
            for intrin in intrinsics
        )
        # print("has_intrinsic", has_intrinsic)
        if has_intrinsic:
            return
        operands = instr_def.operands
        # print("operands", operands)
        # is_noop = check_noop(instr_def.operation)
        num_ins = len(
            [
                op
                for op in instr_def.operands.values()
                if Seal5OperandAttribute.IN in op.attributes or Seal5OperandAttribute.INOUT in op.attributes
            ]
        )
        num_outs = len(
            [
                op
                for op in instr_def.operands.values()
                if Seal5OperandAttribute.OUT in op.attributes or Seal5OperandAttribute.INOUT in op.attributes
            ]
        )
        attributes = instr_def.attributes
        int_types_only = all(op.ty.is_int for op in instr_def.operands.values())
        may_load = Seal5InstrAttribute.MAY_LOAD in attributes
        may_store = Seal5InstrAttribute.MAY_STORE in attributes
        # is_rvc = instr_def.size != 32
        is_branch = arch.InstrAttribute.COND in attributes or arch.InstrAttribute.NO_CONT in attributes
        # has_loop = Seal5InstrAttribute.HAS_LOOP in attributes
        # TODO: has_static_loop
        # has_call = Seal5InstrAttribute.HAS_CALL in attributes
        uses_custom_reg = len(attributes.get(Seal5InstrAttribute.USES, []))
        defs_custom_reg = len(attributes.get(Seal5InstrAttribute.DEFS, []))
        # TODO: check for other side_effects
        sorted_operands = operands  # TODO: sort operands according to asm syntax?
        # print("sorted_operands", sorted_operands)
        supports_intrinsics = (
            (num_outs == 1)  # TODO: handle
            and (num_ins > 0)  # TODO: check if required
            and not may_load  # TODO: handle
            and not may_store  # TODO: handle
            and not is_branch
            and not uses_custom_reg  # TODO: handle
            and not defs_custom_reg  # TODO: handle
            and int_types_only  # TODO: support float,...
        )
        # print("supports_intrinsics", supports_intrinsics)
        if not supports_intrinsics:
            return
        mnemonic = instr_def.mnemonic
        intrinsic_name = mnemonic.replace(".", "_").lower()
        ret_type = None
        ret_signed = None
        args = []
        for op_name, op_def in sorted_operands.items():
            is_out = Seal5OperandAttribute.OUT in op_def.attributes
            is_imm = Seal5OperandAttribute.IS_IMM in op_def.attributes
            is_reg = Seal5OperandAttribute.IS_REG in op_def.attributes
            if is_out:
                assert is_reg
                op_ty = op_def.reg_ty
                signed = op_ty.is_signed_int
                width = op_ty.width
                width = next_power_of_two_ge_8(width)
                supported_width = [8, 16, 32, 64]
                assert width in supported_width, f"Unsupported width: {width}"
                ret_type = f"i{width}"
                ret_signed = signed
                continue
            arg_name = op_name.lower()
            assert is_imm or is_reg
            op_ty = op_def.ty if is_imm else op_def.reg_ty
            # print("op_ty", op_ty)
            assert op_ty.is_int
            assert op_ty.is_scalar
            signed = op_ty.is_signed_int
            width = op_ty.width
            width = next_power_of_two_ge_8(width)
            supported_width = [8, 16, 32, 64]
            assert width in supported_width, f"Unsupported width: {width}"
            arg_type = f"i{width}"
            arg = IntrinsicArg(arg_name, arg_type, is_imm, signed)
            args.append(arg)
        already_exists = any(
            intrin.set_name == set_name.lower() and intrin.intrin_name == intrinsic_name for intrin in intrinsics
        )
        assert not already_exists, f"Intrinsic already exists: {intrinsic_name}"
        intrin = IntrinsicDefn(instr_name, intrinsic_name, set_name, ret_type, ret_signed, args)
        # print("intrin", intrin)
        intrinsics.append(intrin)
        assert ret_type is not None
        assert ret_signed is not None
        assert len(intrinsics) > 0
        intrinsics_settings.intrinsics = intrinsics

    for set_name, set_def in model_obj.sets.items():
        logger.debug("generating auto intrincics for set %s", set_def.name)
        for _, instr_def in set_def.instructions.items():
            logger.debug("generating auto intrincics for instr %s", instr_def.name)
            try:
                handle(instr_def, instrinsics_settings, set_name)
            except Exception as ex:
                if args.skip_failing:
                    logger.warning("Transformation failed for instr %s", instr_def.name)
                else:
                    raise ex

    print("instrinsics_settings_new", instrinsics_settings)

    dump_model(model_obj, out_path)


def main(argv):
    parser = get_parser()
    args = parser.parse_args(argv)
    run(args)


if __name__ == "__main__":
    main(sys.argv[1:])

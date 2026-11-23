# SPDX-License-Identifier: Apache-2.0
#
# This file is part of the M2-ISA-R project: https://github.com/tum-ei-eda/M2-ISA-R
#
# Copyright (C) 2022
# Chair of Electrical Design Automation
# Technical University of Munich

"""Clean M2-ISA-R/Seal5 metamodel to .core_desc file."""

import argparse
from copy import deepcopy
import pathlib

from m2isar.logging import add_logging_args, handle_logging_args
from m2isar.metrics import add_metrics_args, init_metrics, handle_metrics
from m2isar.backends.coredsl2.writer import write_cdsl_splitted, write_cdsl_default

from seal5.model_utils import load_model
from seal5.model import Seal5OperandAttribute
from seal5.transform.normalize_register_pairs import NormalizeRegisterPairs
from seal5.transform.lower_register_pair_views import LowerRegisterPairViews
from seal5.register_pairs import is_pair_bank, legal_pair_operation
from seal5.logging import Logger

from .utils import Seal5CoreDSL2Writer

logger = Logger("backends.coredsl2_writer")


ALLOWED_SEAL5_ATTRS = {
    "is_branch_offs",
    "is_unsigned",
    "is_signed",
    "is_imm",
    "is_reg",
    "in",
    "out",
    "inout",
    "is_32_bit",
    "llvm_type",
    "has_side_effects",
    "llvm_instr",
    "is_unroll_imm",
}


def main():
    """Main app entrypoint."""

    # read command line args
    parser = argparse.ArgumentParser()
    parser.add_argument("top_level", help="A .m2isarmodel or .seal5model file.")
    parser.add_argument("--output", "-o", type=str, required=True, default=None)
    parser.add_argument("--reduced", action="store_true", help="Generate pattern-gen compatible syntax")
    parser.add_argument("--splitted", action="store_true", help="Split per set and instruction")
    parser.add_argument("--ext", type=str, default="core_desc", help="Default file extension (if using --splitted)")
    add_logging_args(parser)
    add_metrics_args(parser)
    parser.add_argument("--compat", action="store_true")
    parser.add_argument(
        "--architectural", action="store_true", help="Export standard CoreDSL with shared X storage and traps"
    )
    args = parser.parse_args()
    if args.architectural and args.reduced:
        parser.error("--architectural cannot be combined with --reduced")

    handle_logging_args(args)  # TODO: pass logger

    # resolve model paths
    top_level = pathlib.Path(args.top_level)
    if args.output is None:
        out_path = f"{top_level}.{args.ext}"
    else:
        out_path = pathlib.Path(args.output)

    model_obj = load_model(top_level, compat=args.compat)
    if args.reduced:
        from seal5.transform.detect_branches import pattern_branch_operation

        for set_def in model_obj.sets.values():
            for instr in set_def.instructions.values():
                instr.operation = pattern_branch_operation(instr.operation, instr.constraints)
                pairs = [
                    name
                    for name, operand in instr.operands.items()
                    if operand.attributes.get(Seal5OperandAttribute.REG_CLASS) == "GPRPair"
                ]
                if pairs:
                    if set_def.xlen != 32:
                        raise ValueError("XP emission requires RV32")
                    instr.operation = NormalizeRegisterPairs(pairs).generate(
                        legal_pair_operation(deepcopy(instr.operation), set(pairs))
                    )

    else:
        model_obj = deepcopy(model_obj)
        for set_def in model_obj.sets.values():
            for key, value in getattr(set_def, "pair_source_state", {}).items():
                setattr(set_def, key, value)
            for instr in set_def.instructions.values():
                instr.operation = getattr(instr, "pair_source_operation", instr.operation)
                instr.operation = LowerRegisterPairViews(set_def.register_banks, instr.vars).generate(instr.operation)
            set_def.register_banks = {
                name: bank for name, bank in set_def.register_banks.items() if not is_pair_bank(bank)
            }
            if args.architectural:
                # The resolved state already includes inherited declarations.
                set_def.extension = []

    metrics = init_metrics()
    allowed_attrs = ALLOWED_SEAL5_ATTRS
    writer_cls = Seal5CoreDSL2Writer
    writer_kwargs = {
        "reduced": args.reduced,
        "allowed_attrs": allowed_attrs,
        "version": "coredsl2" if args.architectural else "seal5",
    }

    if args.splitted:
        metrics = write_cdsl_splitted(
            model_obj,
            out_path=out_path,
            ext=args.ext,
            metrics=metrics,
            writer_cls=writer_cls,
            writer_kwargs=writer_kwargs,
        )
    else:
        metrics = write_cdsl_default(
            model_obj, out_path=out_path, metrics=metrics, writer_cls=writer_cls, writer_kwargs=writer_kwargs
        )
    handle_metrics(metrics, dest=args.metrics, ignore_failing=args.ignore_failing)


if __name__ == "__main__":
    main()

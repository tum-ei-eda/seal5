# SPDX-License-Identifier: Apache-2.0
#
# This file is part of the M2-ISA-R project: https://github.com/tum-ei-eda/M2-ISA-R
#
# Copyright (C) 2022
# Chair of Electrical Design Automation
# Technical University of Munich

"""Clean M2-ISA-R/Seal5 metamodel to .core_desc file."""

import copy
import argparse
import logging
import pathlib

import pandas as pd

from m2isar.backends.coredsl2.utils import CoreDSL2Writer
from m2isar.backends.coredsl2.visitor import CDSLWriterVisitor
from m2isar.logging import add_logging_args, handle_logging_args
from m2isar.metrics import add_metrics_args, init_metrics, handle_metrics
from m2isar.metamodel import arch, behav

from seal5.model_utils import load_model

from .utils import Seal5CoreDSL2Writer

from seal5.logging import Logger

logger = Logger("backends.coredsl2_writer")


ALLOWED_SEAL5_ATTRS = {"is_unsigned", "is_signed", "is_imm", "is_reg", "in", "out", "inout", "is_32_bit", "llvm_type", "has_side_effects", "llvm_instr"}


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
    args = parser.parse_args()

    # initialize logging
    handle_logging_args(args)
    logger.setLevel(getattr(logging, args.log.upper()))

    # resolve model paths
    top_level = pathlib.Path(args.top_level)
    if args.output is None:
        out_path = f"{top_level}.{args.ext}"
    else:
        out_path = pathlib.Path(args.output)

    model_obj = load_model(top_level, compat=args.compat)

    # preprocess model
    # print("model", model)
    metrics = {
        "n_sets": 0,
        "n_instructions": 0,
        "n_skipped": 0,
        "n_failed": 0,
        "n_success": 0,
        "skipped_instructions": [],
        "failed_instructions": [],
        "success_instructions": [],
        "skipped_sets": [],
        "failed_sets": [],
        "success_sets": [],
    }
    if args.splitted:
        assert out_path.is_dir(), "Expecting output directory when using --splitted"
        for set_name, set_def in model_obj.sets.items():
            metrics["n_sets"] += 1
            for instr_def in set_def.instructions.values():
                metrics["n_instructions"] += 1
                allowed_attrs = ALLOWED_SEAL5_ATTRS
                writer = Seal5CoreDSL2Writer(CDSLWriterVisitor(), reduced=args.reduced, allowed_attrs=allowed_attrs, version="seal5")
                logger.debug("writing instr %s/%s", set_def.name, instr_def.name)
                set_def_ = copy.deepcopy(set_def)
                set_def_.instructions = {
                    key: instr_def
                    for key, instr_def_ in set_def.instructions.items()
                    if instr_def.name == instr_def_.name
                }
                try:
                    # TODO: drop_ununsed
                    writer.write_set(set_def_)
                    content = writer.text
                    out_path_ = out_path / set_name / f"{instr_def.name}.{args.ext}"
                    out_path_.parent.mkdir(exist_ok=True)
                    with open(out_path_, "w", encoding="utf-8") as f:
                        f.write(content)
                    metrics["n_success"] += 1
                    metrics["success_instructions"].append(instr_def.name)
                except Exception as ex:
                    logger.exception(ex)
                    metrics["n_failed"] += 1
                    metrics["failed_instructions"].append(instr_def.name)
    else:
        writer = Seal5CoreDSL2Writer(CDSLWriterVisitor(), reduced=args.reduced, version="seal5")
        for set_name, set_def in model_obj.sets.items():
            metrics["n_sets"] += 1
            logger.debug("writing set %s", set_def.name)
            try:
                writer.write_set(set_def)
                metrics["n_success"] += 1
                metrics["success_sets"].append(set_name)
                # TODO: add instrs as well?
            except Exception as ex:
                logger.exception(ex)
                metrics["n_failed"] += 1
                metrics["failed_sets"].append(set_name)
        content = writer.text
        with open(out_path, "w", encoding="utf-8") as f:
            f.write(content)

    if args.metrics is not None:
        pd.DataFrame({key: [val] for key, val in metrics.items()}).to_csv(args.metrics, index=False)
    if not args.ignore_failing and metrics["n_failed"] > 0:
        raise RuntimeError(f"Abort due to errors: {metrics['n_failed']} failed set(s)")


if __name__ == "__main__":
    main()

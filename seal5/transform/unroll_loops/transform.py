"""Full-unroll eligible loops in opted-in Seal5 instructions."""

import argparse
import logging
import pathlib
import sys

import pandas as pd

from seal5.logging import Logger
from seal5.model import Seal5InstrAttribute
from seal5.model_utils import dump_model, load_model

from .visitor import FullLoopUnroller

logger = Logger("transform.unroll_loops")


def get_parser():
    parser = argparse.ArgumentParser()
    parser.add_argument("top_level", help="A .seal5model file.")
    parser.add_argument("--log", default="info", choices=["critical", "error", "warning", "info", "debug"])
    parser.add_argument("--output", "-o", default=None)
    parser.add_argument("--metrics", default=None)
    parser.add_argument("--max-trip-count", type=int, default=32)
    parser.add_argument("--compat", action="store_true")
    return parser


def run(args):
    logger.setLevel(getattr(logging, args.log.upper()))
    top_level = pathlib.Path(args.top_level)
    out_path = top_level.parent / top_level.stem if args.output is None else args.output
    model_obj = load_model(top_level, compat=args.compat)
    metrics = {"n_instructions": 0, "n_opted_in": 0, "n_loops_unrolled": 0}
    for set_def in model_obj.sets.values():
        for instr_def in set_def.instructions.values():
            metrics["n_instructions"] += 1
            if Seal5InstrAttribute.AUTO_UNROLL_LOOP not in instr_def.attributes:
                continue
            metrics["n_opted_in"] += 1
            instr_def.attributes.pop(Seal5InstrAttribute.AUTO_UNROLL_LOOP)
            unroller = FullLoopUnroller(args.max_trip_count)
            unroller.run(instr_def.operation)
            metrics["n_loops_unrolled"] += unroller.unrolled
            logger.info("Full-unrolled %d loop(s) in %s", unroller.unrolled, instr_def.name)
    dump_model(model_obj, out_path, compat=args.compat)
    if args.metrics:
        pd.DataFrame({key: [value] for key, value in metrics.items()}).to_csv(args.metrics, index=False)


def main(argv):
    run(get_parser().parse_args(argv))


if __name__ == "__main__":
    main(sys.argv[1:])

# SPDX-License-Identifier: Apache-2.0
#
# This file is part of the M2-ISA-R project: https://github.com/tum-ei-eda/M2-ISA-R
#
# Copyright (C) 2022
# Chair of Electrical Design Automation
# Technical University of Munich

"""Status report writer for Seal5."""

import argparse
import logging
import pathlib
from collections import defaultdict

import yaml
import pandas as pd

from seal5.settings import Seal5Settings

logger = logging.getLogger("status_writer")


def main():
    """Main app entrypoint."""

    # read command line args
    parser = argparse.ArgumentParser()
    # parser.add_argument("top_level", nargs="+", help="A .m2isarmodel or .seal5model file.")
    parser.add_argument("--log", default="info", choices=["critical", "error", "warning", "info", "debug"])
    parser.add_argument("--output", "-o", type=str, default=None)
    parser.add_argument("--fmt", type=str, choices=["auto", "csv", "pkl", "md"], default="auto")
    parser.add_argument("--yaml", type=str, default=None)
    parser.add_argument("--agg", action="store_true")
    parser.add_argument("--print-df", action="store_true")
    args = parser.parse_args()

    # initialize logging
    logging.basicConfig(level=getattr(logging, args.log.upper()))

    # if args.output is None:
    #     assert top_level.suffix in [".m2isarmodel", ".seal5model"], "Can not infer model type from file extension."
    #     raise NotImplementedError

    #     # out_path = top_level.parent / (top_level.stem + ".core_desc")
    # else:
    assert args.output is not None
    out_path = pathlib.Path(args.output)

    assert args.yaml is not None
    assert pathlib.Path(args.yaml).is_file()
    settings = Seal5Settings.from_yaml_file(args.yaml)
    meta_dir = pathlib.Path(settings.meta_dir)
    # TODOL combine stats automnatically via metrics?
    temp_dir = meta_dir / "temp"
    assert temp_dir.is_dir()
    # all_data = {}
    all_data = []
    agg_data = defaultdict(int)
    for p in temp_dir.rglob("**/*.td.stats"):
        instr_name = p.name.split(".td", 1)[0]
        # print("instr_name", instr_name)
        with open(p, "r") as f:
            data = yaml.safe_load(f)
        assert "pattern-gen" in data
        data = data["pattern-gen"]
        # print("data", data)
        # all_data[instr_name] = data
        all_data.append({"instr_name": instr_name, **data})
        for key, val in data.items():
            agg_data[key] += val

    all_df = pd.DataFrame(all_data)
    agg_df = pd.Series(agg_data).to_frame().reset_index().rename(columns={"index": "stat", 0: "count"})

    df = agg_df if args.agg else all_df
    if args.print_df:
        print(df)

    fmt = args.fmt
    if fmt == "auto":
        fmt = out_path.suffix
        assert len(fmt) > 1
        fmt = fmt[1:].lower()

    if fmt == "csv":
        df.to_csv(out_path, index=False)
    elif fmt == "pkl":
        df.to_pickle(out_path)
    elif fmt == "md":
        df.to_markdown(out_path, index=False)
    else:
        raise ValueError(f"Unsupported fmt: {fmt}")


if __name__ == "__main__":
    main()

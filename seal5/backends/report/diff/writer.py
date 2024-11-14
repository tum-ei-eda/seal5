# SPDX-License-Identifier: Apache-2.0
#
# This file is part of the M2-ISA-R project: https://github.com/tum-ei-eda/M2-ISA-R
#
# Copyright (C) 2022
# Chair of Electrical Design Automation
# Technical University of Munich

"""Diff report writer for Seal5."""

import argparse
import logging
import pathlib

import pandas as pd

from seal5.settings import Seal5Settings

logger = logging.getLogger("diff_writer")


def main():
    """Main app entrypoint."""

    # read command line args
    parser = argparse.ArgumentParser()
    parser.add_argument("--log", default="info", choices=["critical", "error", "warning", "info", "debug"])
    parser.add_argument("--output", "-o", type=str, default=None)
    parser.add_argument("--fmt", type=str, choices=["auto", "csv", "pkl", "md", "mermaid"], default="auto")
    parser.add_argument("--yaml", type=str, default=None)
    # TODO: extract info per patch/model
    args = parser.parse_args()

    # initialize logging
    logging.basicConfig(level=getattr(logging, args.log.upper()))

    assert args.output is not None
    out_path = pathlib.Path(args.output)
    assert args.yaml is not None
    assert pathlib.Path(args.yaml).is_file()
    settings = Seal5Settings.from_yaml_file(args.yaml)

    def process_metrics(settings, ignore_passes: bool = False):
        metrics = settings.metrics
        assert metrics is not None
        assert isinstance(metrics, list)
        ret = []
        for stage_metrics in metrics:
            assert isinstance(stage_metrics, dict)
            assert len(stage_metrics) == 1
            stage_name = list(stage_metrics.keys())[0]
            stage_metrics = list(stage_metrics.values())[0]
            assert isinstance(stage_metrics, dict)
            if stage_name == "deploy":
                n_files_changed = stage_metrics.get("n_files_changed", None)
                n_insertions = stage_metrics.get("n_insertions", None)
                n_deletions = stage_metrics.get("n_deletions", None)
                new = {
                    "phase": "*",
                    "n_files_changed": n_files_changed,
                    "n_insertions": n_insertions,
                    "n_deletions": n_deletions,
                }
                ret.append(new)
                continue
            if stage_name != "patch":
                continue
            phases = stage_metrics.get("stages", None)
            if phases is None:
                continue
            assert isinstance(phases, dict)
            for phase_name, phase_metrics in phases.items():
                n_files_changed = phase_metrics.get("n_files_changed", None)
                n_insertions = phase_metrics.get("n_insertions", None)
                n_deletions = phase_metrics.get("n_deletions", None)
                new = {
                    "phase": phase_name,
                    "n_files_changed": n_files_changed,
                    "n_insertions": n_insertions,
                    "n_deletions": n_deletions,
                }
                ret.append(new)
        return ret

    diff_data = process_metrics(settings)

    diff_df = pd.DataFrame(diff_data)

    fmt = args.fmt
    if fmt == "auto":
        fmt = out_path.suffix
        assert len(fmt) > 1
        fmt = fmt[1:].lower()

    if fmt == "csv":
        diff_df.to_csv(out_path, index=False)
    elif fmt == "pkl":
        diff_df.to_pickle(out_path)
    elif fmt == "md":
        # diff_df.to_markdown(out_path, tablefmt="grid", index=False)
        diff_df.to_markdown(out_path, index=False)
    else:
        raise ValueError(f"Unsupported fmt: {fmt}")


if __name__ == "__main__":
    main()

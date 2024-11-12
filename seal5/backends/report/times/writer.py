# SPDX-License-Identifier: Apache-2.0
#
# This file is part of the M2-ISA-R project: https://github.com/tum-ei-eda/M2-ISA-R
#
# Copyright (C) 2022
# Chair of Electrical Design Automation
# Technical University of Munich

"""Stage times report writer for Seal5."""

import argparse
import logging
import pathlib

import pandas as pd

from seal5.settings import Seal5Settings

logger = logging.getLogger("times_writer")


def main():
    """Main app entrypoint."""

    # read command line args
    parser = argparse.ArgumentParser()
    parser.add_argument("--log", default="info", choices=["critical", "error", "warning", "info", "debug"])
    parser.add_argument("--output", "-o", type=str, default=None)
    parser.add_argument("--fmt", type=str, choices=["auto", "csv", "pkl", "md", "mermaid"], default="auto")
    parser.add_argument("--yaml", type=str, default=None)
    parser.add_argument("--pass-times", action="store_true")
    parser.add_argument("--sum-level", type=int, default=None)
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
        # stage_times = []
        # pass_times = []
        # for stage_metrics in metrics:
        #     assert isinstance(stage_metrics, dict)
        #     assert len(stage_metrics) == 1
        #     stage_name = list(stage_metrics.keys())[0]
        #     stage_metrics = list(stage_metrics.values())[0]
        #     assert isinstance(stage_metrics, dict)
        #     time_s = stage_metrics.get("time_s", None)
        #     start = stage_metrics.get("start", None)
        #     end = stage_metrics.get("end", None)
        #     if time_s:
        #         new = (stage_name, start, end, time_s)
        #         stage_times.append(new)
        #     if not ignore_passes:
        #         pass

        def traverse(x, prefix=None):
            assert isinstance(x, dict)
            assert len(x) == 1
            name = list(x.keys())[0]
            prefix = name if prefix is None else f"{prefix}.{name}"
            y = list(x.values())[0]
            assert isinstance(y, dict)
            passes = y.pop("passes", None)
            if passes is None:
                passes = []
            assert isinstance(passes, list)
            # ret = {}
            ret = []
            for pass_ in passes:
                ret_ = traverse(pass_, prefix=prefix)
                # ret.update(ret_)
                ret.extend(ret_)
            models = y.pop("models", None)
            if models is None:
                models = []
            assert isinstance(models, list)
            for model in models:
                ret2_ = traverse(model, prefix=prefix)
                ret.extend(ret2_)
            ret.append((prefix, y))
            return ret

        all_metrics = []
        for stage_metrics in metrics:
            result = traverse(stage_metrics)
            all_metrics.extend(result)
        filtered_metrics = [
            (x, {k: v for k, v in y.items() if k in ["time_s", "start", "end"]}) for x, y in all_metrics
        ]
        filtered_metrics = [(x, y) for x, y in filtered_metrics if len(y) > 0]
        filtered_metrics = [
            (x, {"time_s": y.get("time_s"), "start": y.get("start"), "end": y.get("end")}) for x, y in filtered_metrics
        ]
        stage_metrics = [{"stage": x, **y} for x, y in filtered_metrics if "." not in x]
        pass_metrics = [{"pass": x.split(".", 1)[-1], **y} for x, y in filtered_metrics if "." in x]
        return stage_metrics, pass_metrics

    stage_times, pass_times = process_metrics(settings, ignore_passes=not args.pass_times)

    stage_times_df = pd.DataFrame(stage_times).sort_values("start")

    if args.pass_times:
        pass_times_df = pd.DataFrame(pass_times).sort_values("start")
        if args.sum_level:
            pass_times_df["pass"] = pass_times_df["pass"].apply(lambda x: ".".join(x.split(".")[: args.sum_level]))
            pass_times_df = pass_times_df.groupby("pass", as_index=False).agg({"start": "min", "end": "max"})
            pass_times_df["time_s"] = pass_times_df["end"] - pass_times_df["start"]
            pass_times_df.sort_values("start", inplace=True)
        times_df = pd.concat([stage_times_df, pass_times_df])
    else:
        times_df = stage_times_df

    fmt = args.fmt
    if fmt == "auto":
        fmt = out_path.suffix
        assert len(fmt) > 1
        fmt = fmt[1:].lower()

    if fmt == "csv":
        times_df.to_csv(out_path, index=False)
    elif fmt == "pkl":
        times_df.to_pickle(out_path)
    elif fmt == "md":
        # times_df.to_markdown(out_path, tablefmt="grid", index=False)
        times_df.to_markdown(out_path, index=False)
    elif fmt == "mermaid":
        content = ""
        content += """gantt
  title Seal5
  dateFormat x
  axisFormat %H:%M:%S
  section Stages

"""
        cur = 0
        for _, stage_data in stage_times_df.iterrows():
            stage = stage_data.get("stage", "?")
            start = stage_data.get("start")
            end = stage_data.get("end")
            time_s = stage_data.get("time_s")
            if start:
                cur = start
            else:
                start = cur

            if end:
                cur = end
            else:
                assert time_s
                cur += time_s
                end = cur
            start = int(start * 1e3)
            end = int(end * 1e3)
            content += f"    {stage} : {start}, {end}\n"
        if args.pass_times:
            content += """
  section Passes

"""
            cur = 0
            for _, pass_data in pass_times_df.iterrows():
                pass_ = pass_data.get("pass", "?")
                start = pass_data.get("start")
                end = pass_data.get("end")
                time_s = pass_data.get("time_s")
                if start:
                    cur = start
                else:
                    start = cur

                if end:
                    cur = end
                else:
                    assert time_s
                    cur += time_s
                    end = cur
                start = int(start * 1e3)
                end = int(end * 1e3)
                content += f"    {pass_} : {start}, {end}\n"
        with open(out_path, "w") as f:
            f.write(content)

    else:
        raise ValueError(f"Unsupported fmt: {fmt}")


if __name__ == "__main__":
    main()

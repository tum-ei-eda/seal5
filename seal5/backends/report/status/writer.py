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

import pandas as pd

from seal5.settings import Seal5Settings
from seal5.model_utils import load_model

logger = logging.getLogger("status_writer")


def main():
    """Main app entrypoint."""

    # read command line args
    parser = argparse.ArgumentParser()
    parser.add_argument("top_level", nargs="+", help="A .m2isarmodel or .seal5model file.")
    parser.add_argument("--log", default="info", choices=["critical", "error", "warning", "info", "debug"])
    parser.add_argument("--output", "-o", type=str, default=None)
    parser.add_argument("--fmt", type=str, choices=["auto", "csv", "pkl", "md"], default="auto")
    parser.add_argument("--yaml", type=str, default=None)
    parser.add_argument("--compact", action="store_true")
    parser.add_argument("--markdown-icons", action="store_true")
    parser.add_argument("--compat", action="store_true")
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

    def process_metrics(settings, model=None):
        metrics = settings.metrics
        assert metrics is not None
        assert isinstance(metrics, list)

        def traverse(x, prefix=None):
            assert isinstance(x, dict)
            assert len(x) == 1
            name = list(x.keys())[0]
            prefix = name if prefix is None else f"{prefix}.{name}"
            y = list(x.values())[0]
            assert isinstance(y, dict)
            y = y.copy()
            passes = y.pop("passes", None)
            if passes is None:
                passes = []
            assert isinstance(passes, list)
            ret = {}
            for pass_ in passes:
                ret_ = traverse(pass_, prefix=prefix)
                ret.update(ret_)
            models = y.pop("models", None)
            if models is None:
                models = []
            assert isinstance(models, list)
            for model in models:
                ret2_ = traverse(model, prefix=prefix)
                ret.update(ret2_)
            for key, value in y.items():
                ret[f"{prefix}.{key}"] = value
            return ret

        all_metrics = {}
        for stage_metrics in metrics:
            result = traverse(stage_metrics)
            all_metrics.update(result)

        def filter_func(x):
            return x.split(".")[-1] in ["success_instructions", "failed_instructions", "skipped_instructions"]

        filtered_metrics = {key: val for key, val in all_metrics.items() if filter_func(key)}
        if model:
            filtered_metrics = {key.replace(f"{model}.", ""): val for key, val in filtered_metrics.items()}
        return filtered_metrics

    def get_status(filtered_metrics, instr_name, invert: bool = False):
        skipped = []
        failed = []
        success = []
        for key, val in filtered_metrics.items():
            if not isinstance(val, list):
                continue
            if instr_name not in val:
                continue
            prefix, metric = key.rsplit(".", 1)
            if metric == "skipped_instructions":
                skipped.append(prefix)
            elif metric == "failed_instructions":
                failed.append(prefix)
            elif metric == "success_instructions":
                success.append(prefix)
        if invert:
            ret = {}
            for pass_name in failed:
                ret[pass_name] = "failed"
            for pass_name in skipped:
                if pass_name in ret:
                    continue
                ret[pass_name] = "skipped"
            for pass_name in success:
                if pass_name in ret:
                    continue
                ret[pass_name] = "success"
        else:
            ret = {
                "skipped": skipped,
                "failed": failed,
                "success": success,
            }
        return ret

    status_data = []

    # resolve model paths
    top_levels = args.top_level
    for top_level in top_levels:
        top_level = pathlib.Path(top_level)
        # abs_top_level = top_level.resolve()

        model_obj = load_model(top_level, compat=args.compat)

        for set_name, set_def in model_obj.sets.items():
            xlen = set_def.xlen
            model = top_level.stem
            filtered_metrics = process_metrics(settings, model=model)

            for instr_def in set_def.instructions.values():
                instr_name = instr_def.name

                data = {
                    "model": model,
                    "set": set_name,
                    "xlen": xlen,
                    "instr": instr_name,
                }
                if not args.compact:
                    for pass_name, pass_status in get_status(filtered_metrics, instr_name, invert=True).items():
                        stage_name, pass_rest = pass_name.split(".", 1)
                        data_ = {**data, "stage": stage_name, "pass": pass_rest, "status": pass_status}
                        status_data.append(data_)
                else:
                    data_ = {**data, **get_status(filtered_metrics, instr_name, invert=False)}
                    data_["n_success"] = len(data_["success"])
                    del data_["success"]
                    data_["n_skipped"] = len(data_["skipped"])
                    del data_["skipped"]
                    data_["n_failed"] = len(data_["failed"])
                    del data_["failed"]
                    data_["n_total"] = data_["n_failed"] + data_["n_skipped"] + data_["n_success"]

                    def helper(success, skipped, failed):
                        if failed:
                            return "bad"
                        if skipped:
                            return "ok"
                        if success:
                            return "good"
                        return "unknown"

                    data_["status"] = helper(data_["n_success"], data_["n_skipped"], data_["n_failed"])
                    status_data.append(data_)
    status_df = pd.DataFrame(status_data)
    fmt = args.fmt
    if fmt == "auto":
        fmt = out_path.suffix
        assert len(fmt) > 1
        fmt = fmt[1:].lower()

    if fmt == "csv":
        status_df.to_csv(out_path, index=False)
    elif fmt == "pkl":
        status_df.to_pickle(out_path)
    elif fmt == "md":
        # status_df.to_markdown(out_path, tablefmt="grid", index=False)
        if args.markdown_icons:

            def helper2(x):
                x = x.replace("success", "success :heavy_check_mark:")
                x = x.replace("skipped", "skipped :question:")
                x = x.replace("failed", "failed :x:")
                x = x.replace("good", "good :green_circle:")
                x = x.replace("ok", "ok :orange_circle:")
                x = x.replace("unknown", "unknown :yellow_circle:")
                x = x.replace("bad", "bad :red_circle:")
                return x

            status_df["status"] = status_df["status"].apply(helper2)
        status_df.to_markdown(out_path, index=False)
    else:
        raise ValueError(f"Unsupported fmt: {fmt}")


if __name__ == "__main__":
    main()

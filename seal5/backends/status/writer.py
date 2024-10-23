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
from seal5.settings import Seal5Settings

logger = logging.getLogger("status_writer")


def main():
    """Main app entrypoint."""

    # read command line args
    parser = argparse.ArgumentParser()
    parser.add_argument("top_level", help="A .m2isarmodel or .seal5model file.")
    parser.add_argument("--log", default="info", choices=["critical", "error", "warning", "info", "debug"])
    parser.add_argument("--output", "-o", type=str, default=None)
    parser.add_argument("--yaml", type=str, default=None)
    args = parser.parse_args()

    # initialize logging
    logging.basicConfig(level=getattr(logging, args.log.upper()))

    # resolve model paths
    top_level = pathlib.Path(args.top_level)
    # abs_top_level = top_level.resolve()

    is_seal5_model = False
    # # print("top_level", top_level)
    # # print("suffix", top_level.suffix)
    if top_level.suffix == ".seal5model":
        is_seal5_model = True
    # if args.output is None:
    #     assert top_level.suffix in [".m2isarmodel", ".seal5model"], "Can not infer model type from file extension."
    #     raise NotImplementedError

    #     # out_path = top_level.parent / (top_level.stem + ".core_desc")
    # else:
    assert args.output is not None
    out_path = pathlib.Path(args.output)

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

    assert args.yaml is not None
    assert pathlib.Path(args.yaml).is_file()
    settings = Seal5Settings.from_yaml_file(args.yaml)

    def process_metrics(settings, model=None):
        metrics = settings.metrics
        assert metrics is not None
        assert isinstance(metrics, list)

        def traverse(x, prefix=None):
            # print("traverse", x, type(x), len(x))
            assert isinstance(x, dict)
            assert len(x) == 1
            name = list(x.keys())[0]
            prefix = name if prefix is None else f"{prefix}.{name}"
            # print("name", name)
            y = list(x.values())[0]
            assert isinstance(y, dict)
            passes = y.pop("passes", None)
            if passes is None:
                passes = []
            assert isinstance(passes, list)
            ret = {}
            for pass_ in passes:
                ret_ = traverse(pass_, prefix=prefix)
                # print("ret_", ret_)
                ret.update(ret_)
            models = y.pop("models", None)
            if models is None:
                models = []
            assert isinstance(models, list)
            for model in models:
                ret2_ = traverse(model, prefix=prefix)
                # print("ret2_", ret2_)
                ret.update(ret2_)
            # print("rest", y)
            for key, value in y.items():
                ret[f"{prefix}.{key}"] = value
            # print("ret", ret)
            # input("!!!123")
            return ret

        all_metrics = {}
        for stage_metrics in metrics:
            result = traverse(stage_metrics)
            all_metrics.update(result)
            # print("result", result)
            # input("!!!")
        print("all_metrics", all_metrics, len(all_metrics))

        def filter_func(x):
            return x.split(".")[-1] in ["success_instructions", "failed_instructions", "skipped_instructions"]

        filtered_metrics = {key: val for key, val in all_metrics.items() if filter_func(key)}
        if model:
            filtered_metrics = {key.replace(f"{model}.", ""): val for key, val in filtered_metrics.items()}
        print("filtered_metrics", filtered_metrics, len(filtered_metrics))
        return filtered_metrics

    def get_status(filtered_metrics, instr_name):
        skipped = []
        failed = []
        success = []
        for key, val in filtered_metrics.items():
            print("key", key)
            print("val", val)
            if not isinstance(val, list):
                print("cont1")
                continue
            if instr_name not in val:
                print("cont2")
                continue
            prefix, metric = key.rsplit(".", 1)
            if metric == "skipped_instructions":
                skipped.append(prefix)
            elif metric == "failed_instructions":
                failed.append(prefix)
            elif metric == "success_instructions":
                success.append(prefix)
            else:
                print("else")
        ret = {
            "skipped": skipped,
            "failed": failed,
            "success": success,
        }
        return ret

    status_data = []
    for set_name, set_def in model["sets"].items():
        print("set_name", set_name)
        xlen = set_def.xlen
        model = top_level.stem
        print("model", model)
        filtered_metrics = process_metrics(settings, model=model)

        for instr_def in set_def.instructions.values():
            instr_name = instr_def.name
            print("instr_name", instr_name)

            data = {
                "model": model,
                "set": set_name,
                "xlen": xlen,
                "instr": instr_name,
                **get_status(filtered_metrics, instr_name),
            }
            status_data.append(data)
    properties_df = pd.DataFrame(status_data)
    properties_df.to_csv(out_path, index=False)


if __name__ == "__main__":
    main()

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
from collections import defaultdict

import pandas as pd

from m2isar.metamodel import arch
from seal5.settings import Seal5Settings

logger = logging.getLogger("test_results_writer")


def main():
    """Main app entrypoint."""

    # read command line args
    parser = argparse.ArgumentParser()
    parser.add_argument("top_level", nargs="+", help="A .m2isarmodel or .seal5model file.")
    parser.add_argument("--log", default="info", choices=["critical", "error", "warning", "info", "debug"])
    parser.add_argument("--output", "-o", type=str, default=None)
    parser.add_argument("--fmt", type=str, choices=["auto", "csv", "pkl", "md"], default="auto")
    parser.add_argument("--yaml", type=str, default=None)
    args = parser.parse_args()

    # initialize logging
    logging.basicConfig(level=getattr(logging, args.log.upper()))

    assert args.yaml is not None
    assert pathlib.Path(args.yaml).is_file()
    settings = Seal5Settings.from_yaml_file(args.yaml)

    def map_tests(metrics):
        test_metrics = None
        for stages_metrics in metrics:
            assert len(stages_metrics) == 1
            if "test" in stages_metrics.keys():
                test_metrics = stages_metrics["test"]
                break
        if test_metrics is None:
            logger.warning("Could not find test metrics. Make sure to run TEST stage!")
            return {}
        ret = defaultdict(list)
        failing = test_metrics.get("failing", None)
        assert failing is not None, "Missing settings.metrics.test.failing"

        def parse_test_filename(fname):
            fname = pathlib.Path(fname)
            suffix = fname.suffix
            assert len(suffix) > 1
            test_fmt = suffix[1:]
            stem = fname.stem
            if stem.count(".") != 1:
                return None
            instr_name, rest = stem.split(".", 1)
            if not rest.startswith("test-"):
                return None
            test_type = rest[5:]
            return instr_name, test_type, test_fmt

        for test_file in failing:
            parsed = parse_test_filename(test_file)
            if parsed is None:
                logger.warning("Could no infer instruction from test file name")
                continue
            instr_name, test_type, test_fmt = parsed
            new = (test_type, test_file, test_fmt, "FAIL")
            ret[instr_name].append(new)
        passed = test_metrics.get("passed", None)
        assert passed is not None, "Missing settings.metrics.test.passed"
        for test_file in passed:
            parsed = parse_test_filename(test_file)
            if parsed is None:
                logger.warning("Could no infer instruction from test file name")
                continue
            instr_name, test_type, test_fmt = parsed
            new = (test_type, test_file, test_fmt, "PASS")
            ret[instr_name].append(new)
        return ret

    metrics = settings.metrics
    tests = map_tests(metrics)

    def filter_tests(tests, instr_name: str):
        assert isinstance(tests, dict)
        candidates = set()
        candidates.add(instr_name)
        candidates.add(instr_name.lower())
        instr_name_alt = instr_name.replace("seal5.", "").replace("SEAL5.", "")
        instr_name_alt = instr_name_alt.replace("seal5_", "").replace("SEAL5_", "")
        instr_name_alt = instr_name_alt.replace(".", "-")
        candidates.add(instr_name_alt)
        candidates.add(instr_name_alt.lower())
        instr_name_alt = instr_name_alt.replace("_", "-")
        candidates.add(instr_name_alt)
        candidates.add(instr_name_alt.lower())

        ret = []
        for candidate_name in candidates:
            ret_ = tests.get(candidate_name, None)
            if ret_ is not None:
                assert isinstance(ret_, list)
                ret.extend(ret_)
        return ret

    results_data = []
    # resolve model paths
    top_levels = args.top_level
    for top_level in top_levels:
        top_level = pathlib.Path(top_level)
        # abs_top_level = top_level.resolve()

        is_seal5_model = False
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


        for set_name, set_def in model["sets"].items():
            xlen = set_def.xlen
            model = top_level.stem

            for instr_def in set_def.instructions.values():
                instr_name = instr_def.name

                data = {
                    "model": model,
                    "set": set_name,
                    "xlen": xlen,
                    "instr": instr_name,
                }
                found_tests = filter_tests(tests, instr_name)
                for test_kind, test_file, test_fmt, test_result in found_tests:
                    data_ = {
                        **data,
                        "test_kind": test_kind,
                        "test_file": test_file,
                        "test_fmt": test_fmt,
                        "result": test_result,
                    }
                    results_data.append(data_)
    results_df = pd.DataFrame(results_data)
    fmt = args.fmt
    if fmt == "auto":
        fmt = out_path.suffix
        assert len(fmt) > 1
        fmt = fmt[1:].lower()

    if fmt == "csv":
        results_df.to_csv(out_path, index=False)
    elif fmt == "pkl":
        results_df.to_pickle(out_path)
    elif fmt == "md":
        # results_df.to_markdown(out_path, tablefmt="grid", index=False)
        results_df.to_markdown(out_path, index=False)
    else:
        raise ValueError(f"Unsupported fmt: {fmt}")


if __name__ == "__main__":
    main()

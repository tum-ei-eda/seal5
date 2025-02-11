# SPDX-License-Identifier: Apache-2.0
#
# This file is part of the M2-ISA-R project: https://github.com/tum-ei-eda/M2-ISA-R
#
# Copyright (C) 2022
# Chair of Electrical Design Automation
# Technical University of Munich

"""Test results report writer for Seal5."""

import argparse
import logging
import pathlib
from collections import defaultdict

import pandas as pd

from seal5.settings import Seal5Settings
from seal5.model import Seal5InstrAttribute
from seal5.model_utils import load_model

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
    parser.add_argument("--compact", action="store_true")
    parser.add_argument("--markdown-icons", action="store_true")
    parser.add_argument("--coverage", default=None)
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

    def map_tests(metrics):
        test_metrics = None
        for stages_metrics in metrics:
            assert len(stages_metrics) == 1
            if "test" in stages_metrics.keys():
                test_metrics = stages_metrics["test"]
                break
        if test_metrics is None:
            logger.warning("Could not find test metrics. Make sure to run TEST stage!")
            return {}, []
        ret = defaultdict(list)
        ret2 = []
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
            if not rest.startswith("test"):
                return None
            test_type = rest[5:]
            if len(test_type) == 0:
                test_type = None
            return instr_name, test_type, test_fmt

        for test_file in failing:
            parsed = parse_test_filename(test_file)
            if parsed is None:
                logger.warning("Could no infer instruction from test file name")
                new = (test_file, "FAIL")
                ret2.append(new)
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
                new = (test_file, "PASS")
                ret2.append(new)
                continue
            instr_name, test_type, test_fmt = parsed
            new = (test_type, test_file, test_fmt, "PASS")
            ret[instr_name].append(new)
        return ret, ret2

    metrics = settings.metrics
    instr_tests, other_tests = map_tests(metrics)
    used_keys = set()

    def filter_tests_by_instr(tests, instr_def):
        instr_name = instr_def.name
        mnemonic = instr_def.mnemonic
        assert isinstance(tests, dict)
        candidates = set()
        candidates.add(instr_name)
        candidates.add(instr_name.lower())
        candidates.add(mnemonic)
        candidates.add(mnemonic.lower())
        instr_name_alt = instr_name.replace("seal5.", "").replace("SEAL5.", "")
        instr_name_alt = instr_name_alt.replace("seal5_", "").replace("SEAL5_", "")
        instr_name_alt = instr_name_alt.replace(".", "-")
        candidates.add(instr_name_alt)
        candidates.add(instr_name_alt.lower())
        mnemonic_alt = mnemonic.replace("seal5.", "").replace("SEAL5.", "")
        mnemonic_alt = mnemonic_alt.replace("seal5_", "").replace("SEAL5_", "")
        mnemonic_alt = mnemonic_alt.replace(".", "-")
        candidates.add(mnemonic_alt)
        candidates.add(mnemonic_alt.lower())
        instr_name_alt = instr_name_alt.replace("_", "-")
        candidates.add(instr_name_alt)
        candidates.add(instr_name_alt.lower())
        mnemonic_alt = mnemonic_alt.replace("_", "-")
        candidates.add(mnemonic_alt)
        candidates.add(mnemonic_alt.lower())

        ret = []
        used = set()
        for candidate_name in candidates:
            ret_ = tests.get(candidate_name, None)
            if ret_ is not None:
                assert isinstance(ret_, list)
                ret.extend(ret_)
                used.add(candidate_name)
        return ret, used

    def filter_tests_by_set(tests, set_def, settings, model_name):
        set_name = set_def.name
        assert isinstance(tests, dict)
        candidates = set()
        candidates.add(set_name)
        candidates.add(set_name.lower())
        set_name_alt = set_name.replace("_", "")
        candidates.add(set_name_alt)
        candidates.add(set_name_alt.lower())
        if settings:
            model_settings = settings.models[model_name]
            extension_settings = model_settings.extensions.get(set_name)
            if extension_settings:
                arch = extension_settings.get_arch(set_name)
                feature = extension_settings.get_feature(set_name)
                candidates.add(arch)
                candidates.add(feature)
                candidates.add(arch.lower())
                candidates.add(feature.lower())
                arch_alt = arch.replace("_", "")
                feature_alt = feature.replace("_", "")
                candidates.add(arch_alt)
                candidates.add(feature_alt)
                candidates.add(arch_alt.lower())
                candidates.add(feature_alt.lower())

        ret = []
        used = set()
        for candidate_name in candidates:
            ret_ = tests.get(candidate_name, None)
            if ret_ is not None:
                assert isinstance(ret_, list)
                ret.extend(ret_)
                used.add(candidate_name)
        return ret, used

    results_data = []
    if args.coverage:
        coverage_data = []
    # resolve model paths
    top_levels = args.top_level
    for top_level in top_levels:
        top_level = pathlib.Path(top_level)

        model_obj = load_model(top_level, compat=args.compat)

        for set_name, set_def in model_obj.sets.items():
            xlen = set_def.xlen
            model_name = top_level.stem

            for instr_def in set_def.instructions.values():
                instr_name = instr_def.name

                data = {
                    "model": model_name,
                    "set": set_name,
                    "xlen": xlen,
                    "instr": instr_name,
                }

                found_tests, used = filter_tests_by_instr(instr_tests, instr_def)
                if args.coverage:

                    def get_instr_cov(instr_def, tests, settings):
                        skip_pattern_gen = Seal5InstrAttribute.SKIP_PATTERN_GEN in instr_def.attributes
                        has_legalizer_settings = False  # TODO: get from settings

                        def lookup_intrin(instr_name, settings):
                            if settings.intrinsics is None:
                                return None
                            intrinsics = settings.intrinsics.intrinsics
                            if not intrinsics:
                                return None
                            found = None
                            for intrin in intrinsics:
                                if intrin.instr_name == instr_name:
                                    found = intrin
                                    break
                            return found

                        intrin = lookup_intrin(instr_def.name, settings)
                        has_intrin = intrin is not None
                        # (test_kind, test_fmt): optional
                        temp = {
                            ("mc", "s"): True,
                            ("mc-invalid", "s"): False,
                            ("inline-asm", "c"): False,
                            ("cg", "ll"): not skip_pattern_gen,
                            ("cg", "c"): not skip_pattern_gen,
                            ("cg", "mir"): not skip_pattern_gen,
                            ("legalizer", "mir"): has_legalizer_settings,
                            ("intrin", "ll"): has_intrin,
                            ("builtin", "c"): has_intrin,
                        }
                        # (test_kind, test_fmt, optional): (extra, exists)
                        temp2 = {key: (val, False, False) for key, val in temp.items()}
                        for test_kind, test_file, test_fmt, test_result in found_tests:
                            required = temp.get((test_kind, test_fmt), None)
                            if required is not None:
                                temp2[(test_kind, test_fmt)] = (required, False, True)
                            else:
                                temp2[(test_kind, test_fmt)] = (False, True, True)
                        # (test_kind, test_fmt, optional, extra, exists)
                        ret = [(*key, *val) for key, val in temp2.items()]
                        return ret

                    instr_cov = get_instr_cov(instr_def, found_tests, settings)
                    for test_kind, test_fmt, required, extra, exists in instr_cov:

                        def helper(required, extra, exists):
                            if exists:
                                return "good"
                            if not required:
                                return "ok"
                            return "bad"

                        data_cov = {
                            **data,
                            "test_kind": test_kind,
                            "test_fmt": test_fmt,
                            "required": required,
                            "extra": extra,
                            "exists": exists,
                            "coverage": helper(required, extra, exists),
                        }
                        coverage_data.append(data_cov)
                used_keys.update(used)
                for test_kind, test_file, test_fmt, test_result in found_tests:
                    data_ = {
                        **data,
                        "test_kind": test_kind,
                        "test_file": test_file,
                        "test_fmt": test_fmt,
                        "result": test_result,
                    }
                    results_data.append(data_)
            found_tests, used = filter_tests_by_set(instr_tests, set_def, settings, model_name)
            used_keys.update(used)
            data["instr"] = None
            for test_kind, test_file, test_fmt, test_result in found_tests:
                data_ = {
                    **data,
                    "test_kind": test_kind,
                    "test_file": test_file,
                    "test_fmt": test_fmt,
                    "result": test_result,
                }
                results_data.append(data_)

    def get_unused_tests(tests, used_keys):
        ret = sum([val for key, val in tests.items() if key not in used_keys], [])
        return ret

    unused_tests = get_unused_tests(instr_tests, used_keys)

    data = {
        "model": None,
        "set": None,
        "xlen": None,
        "instr": None,
    }

    for test_kind, test_file, test_fmt, test_result in unused_tests:
        data_ = {
            **data,
            "test_kind": test_kind,
            "test_file": test_file,
            "test_fmt": test_fmt,
            "result": test_result,
        }
        results_data.append(data_)

    for test_file, test_result in other_tests:
        test_fmt = pathlib.Path(test_file).suffix[1:]
        test_kind = None
        data_ = {
            **data,
            "test_kind": test_kind,
            "test_file": test_file,
            "test_fmt": test_fmt,
            "result": test_result,
        }
        results_data.append(data_)

    results_df = pd.DataFrame(results_data)

    if args.compact and len(results_df) > 0:
        new = []
        for group, group_df in results_df.groupby(["model", "set", "xlen", "instr"], dropna=False):
            n_tests = len(group_df)
            counts = group_df["result"].value_counts()
            n_pass = counts.get("PASS", 0)
            n_fail = counts.get("FAIL", 0)

            def helper(n_tests, n_pass, n_fail):
                if n_fail:
                    return "bad"
                if n_pass:
                    return "good"
                return "unknown"

            state = helper(n_tests, n_pass, n_fail)
            new_ = {
                "model": group[0],
                "set": group[1],
                "xlen": group[2],
                "instr": group[3],
                "n_pass": n_pass,
                "n_fail": n_fail,
                "n_tests": n_tests,
                "state": state,
            }
            new.append(new_)
        results_df = pd.DataFrame(new)

    if args.coverage:
        # TODO: also add set test coverage
        coverage_df = pd.DataFrame(coverage_data)
        if args.compact and len(coverage_df) > 0:
            new = []
            for group, group_df in coverage_df.groupby(["model", "set", "xlen", "instr"], dropna=False):
                n_exists = group_df["exists"].value_counts().get(True, 0)
                n_required = group_df["required"].value_counts().get(True, 0)
                n_optional = group_df[["required", "extra"]].value_counts().get((False, False), 0)
                n_extra = group_df["extra"].value_counts().get(True, 0)
                n_required_exists = group_df[["required", "exists"]].value_counts().get((True, True), 0)
                n_optional_exists = group_df[["required", "exists"]].value_counts().get((False, True), 0)

                def helper2(n_exists, n_required, n_required_exists, n_optional, n_optional_exists):
                    if n_exists == 0:
                        return "bad"
                    if n_required_exists < n_required:
                        return "bad"
                    assert n_required_exists == n_required
                    if n_optional_exists == n_optional:
                        return "good"
                    return "ok"

                cov = helper2(n_exists, n_required, n_required_exists, n_optional, n_optional_exists)
                new_ = {
                    "model": group[0],
                    "set": group[1],
                    "xlen": group[2],
                    "instr": group[3],
                    "n_exists": n_exists,
                    "n_required": n_required,
                    "n_optional": n_optional,
                    "n_extra": n_extra,
                    "n_required_exists": n_required_exists,
                    "n_optional_exists": n_optional_exists,
                    "coverage": cov,
                }
                new.append(new_)
            coverage_df = pd.DataFrame(new)

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
        if args.markdown_icons and len(results_df) > 0:

            def helper(x):
                x = x.replace("PASS", "PASS :heavy_check_mark:")
                x = x.replace("FAIL", "FAIL :x:")
                x = x.replace("good", "good :green_circle:")
                x = x.replace("ok", "ok :orange_circle:")
                x = x.replace("unknown", "unknown :yellow_circle:")
                x = x.replace("bad", "bad :red_circle:")
                return x

            if args.compact:
                results_df["state"] = results_df["state"].apply(helper)
            else:
                results_df["result"] = results_df["result"].apply(helper)
        results_df.to_markdown(out_path, index=False)
    else:
        raise ValueError(f"Unsupported fmt: {fmt}")

    if args.coverage:
        # TODO: share code
        cov_path = pathlib.Path(args.coverage)
        fmt = args.fmt
        if fmt == "auto":
            fmt = cov_path.suffix
            assert len(fmt) > 1
            fmt = fmt[1:].lower()

        if fmt == "csv":
            coverage_df.to_csv(cov_path, index=False)
        elif fmt == "pkl":
            coverage_df.to_pickle(cov_path)
        elif fmt == "md":
            # coverage_df.to_markdown(cov_path, tablefmt="grid", index=False)
            if args.markdown_icons and len(coverage_df) > 0:

                def helper(x):
                    x = x.replace("good", "good :green_circle:")
                    x = x.replace("ok", "ok :orange_circle:")
                    x = x.replace("unknown", "unknown :yellow_circle:")
                    x = x.replace("bad", "bad :red_circle:")
                    return x

                if args.compact:
                    coverage_df["coverage"] = coverage_df["coverage"].apply(helper)
                else:
                    coverage_df["coverage"] = coverage_df["coverage"].apply(helper)
            coverage_df.to_markdown(cov_path, index=False)
        else:
            raise ValueError(f"Unsupported fmt: {fmt}")


if __name__ == "__main__":
    main()

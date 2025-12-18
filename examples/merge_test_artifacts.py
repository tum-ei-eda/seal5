#
# Copyright (c) 2025 TUM Department of Electrical and Computer Engineering.
# Copyright (c) 2025 DLR-SE Department of System Evolution and Operation
#
# This file is part of Seal5.
# See https://github.com/tum-ei-eda/seal5.git for further info.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#


import argparse
import pathlib

import pandas as pd

# import numpy as np
from seal5.logging import Logger


logger = Logger("examples." + __name__)


def main():
    """Main function."""

    # read command line args
    parser = argparse.ArgumentParser()
    parser = argparse.ArgumentParser(description="Merge SEAL5 Test Results")
    parser.add_argument("status_file", type=str, help="Path to the status file")
    parser.add_argument("properties_file", type=str, help="Path to the file of instruction properties")
    parser.add_argument("test_results", type=str, help="Path to the file containing seal5 test result file name")
    parser.add_argument("test_cv_file", type=str, help="Path to the file containing seal5 test coverage results")
    args = parser.parse_args()

    if args.status_file:
        status_df = pd.read_csv(pathlib.Path(args.status_file))
    else:
        raise RuntimeError("Path to status file must be specified")

    if args.test_results:
        try:
            test_result_df = pd.read_csv(pathlib.Path(args.test_results))
            test_result_df = test_result_df[~pd.isna(test_result_df["instr"])]
        except pd.errors.EmptyDataError:
            logger.warning("Skipping empty file: %s", args.test_results)
            test_result_df = None
    else:
        raise RuntimeError("Path to Test Results file must be specified")

    if args.properties_file:
        props_df = pd.read_csv(pathlib.Path(args.properties_file))
    else:
        raise RuntimeError("Path to Instruction Properties file must be specified")

    if args.test_cv_file:
        test_cv_df = pd.read_csv(pathlib.Path(args.test_cv_file))
    else:
        raise RuntimeError("Path to Test Coverage file must be specified")

    status_props_df = pd.merge(status_df, props_df)
    if test_result_df is not None and len(test_result_df) > 0:
        stat_prop_result_df = pd.merge(
            status_props_df, test_result_df, on=["model", "set", "xlen", "instr"], how="left"
        )
    else:
        stat_prop_result_df = status_props_df

    stat_prop_result_df = stat_prop_result_df.sort_values("model")

    stat_prop_result_df.fillna(value=0, inplace=True)

    if test_cv_df is not None and len(test_cv_df) > 0:
        stat_prop_result_cv_df = pd.merge(
            stat_prop_result_df, test_cv_df, on=["model", "set", "xlen", "instr"], how="left"
        )
    else:
        stat_prop_result_cv_df = stat_prop_result_df

    def save_data_frames_as_html_to_file(dataframe, filename):
        with open(filename, "w", encoding="utf-8") as html_file:
            dataframe.to_html(buf=html_file, index=True)

    def rounded_mean(x):
        return x.mean().round(0).astype(int)

    stat_prop_result_cv_df.set_index(["model", "enc_format", "opcode"], inplace=True)

    stat_prop_result_all = stat_prop_result_cv_df.groupby(level=[0, 1, 2])[
        ["instr", "n_success", "n_failed", "n_skipped", "n_total", "status"]
    ].agg(
        {
            "instr": "unique",
            "status": "unique",
            "n_success": rounded_mean,
            "n_failed": "mean",
            "n_skipped": "mean",
            "n_total": "mean",
        }
    )

    if test_result_df is not None and len(test_result_df) > 0:
        stat_prop_result_cv_test = stat_prop_result_cv_df.groupby(level=[0, 1, 2])[
            ["n_pass", "n_fail", "n_tests", "state"]
        ].agg({"n_pass": rounded_mean, "n_fail": rounded_mean, "n_tests": rounded_mean, "state": "unique"})
    else:
        stat_prop_result_cv_test = None

    if test_cv_df is not None and len(test_cv_df) > 0:
        stat_prop_result_coverage = stat_prop_result_cv_df.groupby(level=[0, 1, 2])[
            ["n_exists", "n_required", "n_optional", "n_required_exists", "n_optional_exists", "coverage"]
        ].agg(
            {
                "n_exists": rounded_mean,
                "n_required": rounded_mean,
                "n_optional": rounded_mean,
                "n_required_exists": rounded_mean,
                "n_optional_exists": rounded_mean,
                "coverage": "unique",
            }
        )
    else:
        stat_prop_result_coverage = None

    def calc_stage_percentage():
        perc_success = (
            ((stat_prop_result_all["n_success"] * 100) / stat_prop_result_all["n_total"]).astype(int)
        ).astype(str)
        perc_skipped = (
            ((stat_prop_result_all["n_skipped"] * 100) / stat_prop_result_all["n_total"]).astype(int)
        ).astype(str)
        perc_failed = (((stat_prop_result_all["n_failed"] * 100) / stat_prop_result_all["n_total"]).astype(int)).astype(
            str
        )

        perc_result = "[" + perc_success + "%" + " / " + perc_skipped + "%" + " / " + perc_failed + "%" + "]"
        return perc_result

    # def calc_stage_percentage_sum():
    #     perc_success = (
    #         ((stat_prop_result_all["n_success"].sum() * 100) / stat_prop_result_all["n_total"].sum()).astype(int)
    #     ).astype(str)
    #     perc_skipped = (
    #         ((stat_prop_result_all["n_skipped"].sum() * 100) / stat_prop_result_all["n_total"].sum()).astype(int)
    #     ).astype(str)
    #     perc_failed = (
    #         ((stat_prop_result_all["n_failed"].sum() * 100) / stat_prop_result_all["n_total"].sum()).astype(int)
    #     ).astype(str)

    #     perc_result = "[" + perc_success + "%" + " / " + perc_skipped + "%" + " / " + perc_failed + "%" + "]"
    #     return perc_result

    def calc_test_percentage():
        perc_pass = (stat_prop_result_cv_test["n_pass"] * 100) / stat_prop_result_cv_test["n_tests"]
        perc_fail = (stat_prop_result_cv_test["n_fail"] * 100) / stat_prop_result_cv_test["n_tests"]
        #       if(np.isnan(perc_pass)):
        #         perc_pass = 0;
        perc_result = "[" + round(perc_pass, 0).astype(str) + "%" + " / " + round(perc_fail, 0).astype(str) + "%" + "]"
        return perc_result

    # def calc_test_percentage_sum():
    #     perc_pass = (
    #         (stat_prop_result_cv_test["n_pass"].sum() * 100) / stat_prop_result_cv_test["n_tests"].sum()
    #     ).astype(int)
    #     perc_fail = (
    #         (stat_prop_result_cv_test["n_fail"].sum() * 100) / stat_prop_result_cv_test["n_tests"].sum()
    #     ).astype(int)

    #     perc_result = "[" + round(perc_pass, 0).astype(str) + "%" + " / " + round(perc_fail, 0).astype(str)
    #         + "%" + "]"
    #     return perc_result

    def calc_coverage_percentage():
        perc_required = (
            (stat_prop_result_coverage["n_required_exists"] * 100) / stat_prop_result_coverage["n_required"]
        ).astype(
            int
        )  # .astype(str
        perc_optional = (
            (stat_prop_result_coverage["n_optional_exists"] * 100) / stat_prop_result_coverage["n_optional"]
        ).astype(
            int
        )  # .astype(str)
        perc_exists = (
            (stat_prop_result_coverage["n_exists"] * 100)
            / (stat_prop_result_coverage["n_required"] + stat_prop_result_coverage["n_optional"])
        ).astype(
            int
        )  # .astype(str)

        perc_result = (
            "["
            + round(perc_required, 0).astype(str)
            + "%"
            + " / "
            + round(perc_optional, 0).astype(str)
            + "%"
            + " / "
            + round(perc_exists, 0).astype(str)
            + "%]"
        )
        return perc_result

    stat_result_summary = (
        stat_prop_result_all["n_success"].astype(str)
        + " / "
        + stat_prop_result_all["n_skipped"].astype(str)
        + " / "
        + stat_prop_result_all["n_failed"].astype(str)
        + " "
        + calc_stage_percentage()
    )
    stat_prop_result_all.insert(loc=1, column="Status_Summary: (Passed/Skipped/Failed) %", value=stat_result_summary)

    if stat_prop_result_cv_test is not None:
        stat_test_summary = (
            stat_prop_result_cv_test["n_pass"].astype(str)
            + " / "
            + stat_prop_result_cv_test["n_fail"].astype(str)
            + " "
            + calc_test_percentage()
        )
        stat_prop_result_cv_test.insert(
            loc=1, column="Summary Test Results: (Passed/Failed) % ", value=stat_test_summary
        )

    if stat_prop_result_coverage is not None:
        stat_prop_coverage_summary = (
            stat_prop_result_coverage["n_required_exists"].astype(str)
            + " : "
            + stat_prop_result_coverage["n_required"].astype(str)
            + " / "
            + stat_prop_result_coverage["n_optional_exists"].astype(str)
            + " : "
            + stat_prop_result_coverage["n_optional"].astype(str)
            + " / "
            + stat_prop_result_coverage["n_exists"].astype(str)
            + " : "
            + (stat_prop_result_coverage["n_optional"] + stat_prop_result_coverage["n_required"]).astype(str)
            + " / "
            + calc_coverage_percentage()
        )
        #   + (stat_prop_result_coverage["n_optional"]+stat_prop_result_coverage["n_required"]).astype(str)+

        stat_prop_result_coverage.insert(
            loc=1,
            column=(
                " Summary Test Results Coverage: (No. Existing Required : No. Required / "
                "No. Optional Existing : No Optional / No. Total Existing Test : No. Total Tests) % "
            ),
            value=stat_prop_coverage_summary,
        )

    final_status_results = (
        stat_prop_result_all.drop("n_success", axis=1)
        .drop("n_failed", axis=1)
        .drop("n_skipped", axis=1)
        .drop("n_total", axis=1)
    )

    if stat_prop_result_cv_test is not None and len(stat_prop_result_cv_test) > 0:
        final_test_results = (
            stat_prop_result_cv_test.drop("n_pass", axis=1).drop("n_fail", axis=1).drop("n_tests", axis=1)
        )
        final_test_table = pd.merge(
            final_status_results, final_test_results, on=["model", "enc_format", "opcode"], how="inner"
        )
    else:
        final_test_table = final_status_results
    if stat_prop_result_coverage is not None and len(stat_prop_result_coverage) > 0:
        final_coverage_results = (
            stat_prop_result_coverage.drop("n_exists", axis=1)
            .drop("n_required", axis=1)
            .drop("n_optional", axis=1)
            .drop("n_required_exists", axis=1)
            .drop("n_optional_exists", axis=1)
        )
        final_coverage_table = pd.merge(
            final_test_table, final_coverage_results, on=["model", "enc_format", "opcode"], how="inner"
        )
    else:
        final_coverage_table = final_test_table

    save_data_frames_as_html_to_file(final_test_table, "Grouped_stat_prop_result_test.html")
    save_data_frames_as_html_to_file(final_coverage_table, "Grouped_stat_prop_result_cv.html")
    save_data_frames_as_html_to_file(stat_prop_result_cv_df, "Grouped_stat_prop_result_all.html")

    final_test_table = final_test_table.drop("instr", axis=1)
    final_coverage_table = final_coverage_table.drop("instr", axis=1)
    save_data_frames_as_html_to_file(final_test_table, "Grouped_stat_prop_result_test_wo_instr.html")
    save_data_frames_as_html_to_file(final_coverage_table, "Grouped_stat_prop_result_cv_wo_instr.html")


#   print("FINAL TEST_RESULTS\n")
#   print(final_test_results)

#    print('FINALE STATUS RESULTS\n')
#    print(final_status_results)


#    print("Final Test Table\n")
#    print(final_test_table)
#    print('finale Coverage Results\n')
#    print(final_coverage_results)
#    print("Final Coverage Table\n")
#    print(final_coverage_table)

if __name__ == "__main__":
    main()

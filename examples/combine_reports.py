import logging
import argparse
import pandas as pd
from pathlib import Path

from seal5.logging import Logger

logger = Logger("examples." + __name__)


def main():
    """Main app entrypoint."""

    # read command line args
    parser = argparse.ArgumentParser()
    parser.add_argument("report_dir", nargs="+", help="Multiple report directories")
    parser.add_argument("--log", default="info", choices=["critical", "error", "warning", "info", "debug"])
    parser.add_argument("--output", "-o", type=str, default=None)
    parser.add_argument("--full", action="store_true")
    parser.add_argument("--fmt", type=str, choices=["auto", "md"], default="md")
    parser.add_argument("--markdown-icons", action="store_true")
    args = parser.parse_args()

    # initialize logging
    logger.setLevel(getattr(logging, args.log.upper()))

    dirs = args.report_dir
    print("dirs", dirs)

    all_names = set()
    test_results_compact_dfs = []
    test_coverage_compact_dfs = []
    status_compact_dfs = []

    for report_dir in dirs:
        report_dir = Path(report_dir)
        # print("report_dir", report_dir)
        assert report_dir.is_dir()
        temp_dir = report_dir
        name = report_dir.name
        while name in [".seal5", "reports"]:
            temp_dir = temp_dir.parent
            name = temp_dir.name
        # print("name", name)
        assert name not in all_names, f"Duplicate name: {name}"
        all_names.add(name)
        test_results_compact_csv = report_dir / "test_results_compact.csv"
        assert test_results_compact_csv.is_file()
        test_results_compact_df = pd.read_csv(test_results_compact_csv)
        if len(test_results_compact_df) > 0:
            test_results_compact_df.insert(0, "Name", name)
            test_results_compact_dfs.append(test_results_compact_df)
        test_coverage_compact_csv = report_dir / "test_coverage_compact.csv"
        assert test_coverage_compact_csv.is_file()
        test_coverage_compact_df = pd.read_csv(test_coverage_compact_csv)
        if len(test_results_compact_df) > 0:
            test_coverage_compact_df.insert(0, "Name", name)
            test_coverage_compact_dfs.append(test_coverage_compact_df)
        status_compact_csv = report_dir / "status_compact.csv"
        assert status_compact_csv.is_file()
        status_compact_df = pd.read_csv(status_compact_csv)
        if len(test_results_compact_df) > 0:
            status_compact_df.insert(0, "Name", name)
            status_compact_dfs.append(status_compact_df)

    all_test_results_compact_df = pd.concat(test_results_compact_dfs)
    all_test_coverage_compact_df = pd.concat(test_coverage_compact_dfs)
    all_status_compact_df = pd.concat(status_compact_dfs)

    IGNORE_GOOD_TESTS = not args.full

    if IGNORE_GOOD_TESTS:
        if len(all_test_results_compact_df) > 0:
            all_test_results_compact_df = all_test_results_compact_df[
                ~all_test_results_compact_df["state"].isin(["good"])
            ]
        if len(all_test_coverage_compact_df) > 0:
            all_test_coverage_compact_df = all_test_coverage_compact_df[
                ~all_test_coverage_compact_df["coverage"].isin(["good"])
            ]
        if len(all_status_compact_df) > 0:
            all_status_compact_df = all_status_compact_df[~all_status_compact_df["status"].isin(["ok", "good"])]

    out_path = args.output

    fmt = args.fmt
    if fmt == "auto":
        assert out_path is not None
        out_path = Path(out_path)
        fmt = out_path.suffix
        assert len(fmt) > 1
        fmt = fmt[1:].lower()

    if fmt == "md":
        # status_df.to_markdown(out_path, tablefmt="grid", index=False)
        # status_df.to_markdown(out_path, index=False)
        label = "Failing" if IGNORE_GOOD_TESTS else "All"
        status_md = all_status_compact_df.to_markdown(index=False)
        test_results_md = all_test_results_compact_df.to_markdown(index=False)
        test_coverage_md = all_test_coverage_compact_df.to_markdown(index=False)
        content = f"""
## {label} Passes

{status_md}

## {label} Test Results

{test_results_md}

## {label} Test Coverage

{test_coverage_md}
"""
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

            content = helper2(content)
    else:
        raise ValueError(f"Unsupported fmt: {fmt}")

    if out_path is None:
        print(content)
    else:
        with open(out_path, "w") as f:
            f.write(content)


if __name__ == "__main__":
    main()

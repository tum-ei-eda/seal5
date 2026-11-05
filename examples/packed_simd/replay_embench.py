#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Retest previously vectorized Embench IR without rerunning the optimizer."""
import argparse
import hashlib
import json
from pathlib import Path

from embench import execute


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--results", required=True, type=Path, help="Earlier run's results.json and artifact directory")
    parser.add_argument("--llvm22-bin", type=Path)
    parser.add_argument("--llvm23-bin", type=Path)
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args()
    data = json.loads(args.results.read_text())
    report = {"input_results": str(args.results.resolve()), "records": []}
    for row in data["records"]:
        binary = getattr(args, f"llvm{row['llvm']}_bin")
        if binary is None or row["variant"] != "packed" or row.get("optimizer_exit") != 0:
            continue
        name = Path(row["source"])
        ir = args.results.resolve().parent / str(row["llvm"]) / name.parent.name / name.stem / "packed/optimized.ll"
        digest = hashlib.sha256(ir.read_bytes()).hexdigest()
        folder = args.output.resolve() / str(row["llvm"]) / name.parent.name / name.stem
        attrs = "+m,+gpr32v,+xpackedsimd32"
        if data.get("memory_model") == "unaligned":
            attrs += ",+unaligned-scalar-mem"
        for selector in (0, 1):
            code, _, diagnostics = execute(
                [
                    binary.resolve() / "llc",
                    "-O3",
                    "-mtriple=riscv32",
                    f"-mattr={attrs}",
                    f"-global-isel={selector}",
                    "-global-isel-abort=1",
                    "-verify-machineinstrs",
                    "-filetype=obj",
                    ir,
                    "-o",
                    folder / f"isel{selector}.o",
                ],
                folder / f"isel{selector}",
            )
            report["records"].append(
                {
                    "llvm": row["llvm"],
                    "source": row["source"],
                    "ir_sha256": digest,
                    "selector": selector,
                    "exit_code": code,
                    "diagnostic": next((x[:512] for x in diagnostics.splitlines() if "LLVM ERROR:" in x), ""),
                }
            )
    if not report["records"]:
        parser.error("No matching optimized IR; specify at least one --llvm*-bin")
    args.output.mkdir(parents=True, exist_ok=True)
    (args.output / "results.json").write_text(json.dumps(report, indent=2) + "\n")
    failures = [r for r in report["records"] if r["exit_code"]]
    for row in failures:
        print(row["llvm"], row["source"], row["selector"], row["diagnostic"])
    print(len(report["records"]) - len(failures), "/", len(report["records"]), "codegen checks passed")


if __name__ == "__main__":
    main()

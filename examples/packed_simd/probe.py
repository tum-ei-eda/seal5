#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Probe ordinary packed-SIMD extraction and legalization without rebuilding LLVM.

This is an investigation tool, not a passing codegen regression suite. A process
returning zero is not sufficient: extraction must contain a vector-typed Pat.
"""
import argparse
from collections import Counter
import json
from pathlib import Path
import re
import subprocess

FIXTURES = Path(__file__).resolve().parent / "fixtures"


def run(command, destination):
    result = subprocess.run(list(map(str, command)), capture_output=True, text=True)
    destination.with_suffix(".stdout").write_text(result.stdout)
    destination.with_suffix(".stderr").write_text(result.stderr)
    return result


def probe(version, binary, output):
    records = []
    for fixture in sorted(FIXTURES.glob("*.core_desc")):
        name = fixture.stem.upper()
        lanes, width = map(int, name.rsplit("_", 1)[1].split("X"))
        for enabled in (False, True):
            attributes = "+m," + ("+gpr32v" if enabled else "-gpr32v")
            folder = output / str(version) / fixture.stem / ("enabled" if enabled else "disabled")
            folder.mkdir(parents=True, exist_ok=True)
            destination = folder / "pattern.td"
            extraction = run(
                [
                    binary / "pattern-gen",
                    fixture,
                    "--no-extend",
                    "--riscv-xlen",
                    "32",
                    f"--mattr={attributes}",
                    "-p",
                    "HasGPR32V,IsRV32",
                    "-o",
                    destination,
                ],
                folder / "extract",
            )
            contents = destination.read_text() if destination.exists() else ""
            failed = "Pattern Generation failed" in extraction.stderr
            vector_pattern = (
                extraction.returncode == 0
                and not failed
                and "def : Pat<" in contents
                and f"v{lanes}i{width}" in contents
                and name in contents
            )
            records.append(
                {
                    "llvm": version,
                    "instruction": name,
                    "gpr32v": enabled,
                    "probe": "tablegen-extraction",
                    "exit_code": extraction.returncode,
                    "vector_pattern": vector_pattern,
                    "diagnostic": extraction.stderr.splitlines()[:2],
                }
            )
            for selector in ("globalisel-legalizer", "selectiondag-codegen"):
                command = [
                    binary / "llc",
                    fixture.with_suffix(".ll"),
                    "-mtriple=riscv32",
                    "-O2",
                    f"-mattr={attributes}",
                    "-verify-machineinstrs",
                    "-o",
                    "-",
                ]
                if selector == "globalisel-legalizer":
                    command += ["-global-isel=1", "-global-isel-abort=1", "-stop-after=legalizer"]
                else:
                    command += ["-global-isel=0"]
                result = run(command, folder / selector)
                records.append(
                    {
                        "llvm": version,
                        "instruction": name,
                        "gpr32v": enabled,
                        "probe": selector,
                        "exit_code": result.returncode,
                        "retains_vector_op": bool(re.search(r"G_(ADD|SUB).*<", result.stdout)),
                        "diagnostic": result.stderr.splitlines()[:2],
                    }
                )
    return records


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--llvm22-bin", type=Path, required=True)
    parser.add_argument("--llvm23-bin", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    args.output.mkdir(parents=True, exist_ok=True)
    records = []
    versions = {}
    for version, binary in ((22, args.llvm22_bin), (23, args.llvm23_bin)):
        versions[str(version)] = subprocess.check_output([str(binary / "llc"), "--version"], text=True)
        records += probe(version, binary.resolve(), args.output)
    report = {"toolchains": versions, "records": records}
    (args.output / "results.json").write_text(json.dumps(report, indent=2) + "\n")
    summary = Counter((r["llvm"], r["probe"], r["exit_code"] == 0) for r in records)
    for (version, kind, success), count in sorted(summary.items()):
        print(f"LLVM {version}: {kind}: {count} processes {'succeeded' if success else 'failed'}")
    print("Vector-typed TableGen patterns:", sum(r.get("vector_pattern", False) for r in records))
    print("Scalar SelectionDAG fallback is not evidence of packed-instruction selection.")
    print("Detailed results:", args.output / "results.json")


if __name__ == "__main__":
    main()

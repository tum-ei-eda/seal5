#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Record pair pattern extraction and native-P/custom-only vectorization probes."""
import argparse
import json
from pathlib import Path
import subprocess
import sys


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--bin", required=True, type=Path)
    parser.add_argument("--model", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args()
    args.output.mkdir(parents=True, exist_ok=True)
    output = args.output.resolve()
    source = output / "input"
    source.mkdir(exist_ok=True)
    subprocess.run(
        [
            sys.executable,
            "-m",
            "seal5.backends.coredsl2.writer",
            args.model,
            "--reduced",
            "--splitted",
            "--output",
            source,
        ],
        check=True,
    )
    records = []

    def record(name, command):
        p = subprocess.run(list(map(str, command)), capture_output=True, text=True)
        (output / f"{name}.stdout").write_text(p.stdout)
        (output / f"{name}.stderr").write_text(p.stderr)
        records.append({"name": name, "command": list(map(str, command)), "exit_code": p.returncode})
        return p

    for cdsl in sorted(source.rglob("*.core_desc")):
        name = cdsl.stem
        record(
            name + "-semantics",
            [
                args.bin / "pattern-gen",
                cdsl,
                "--riscv-xlen=32",
                "--skip-patterns",
                "--skip-formats",
                "-o",
                output / f"{name}.ll",
            ],
        )
        for features in ("+m,+xregpairs", "+m,+experimental-p"):
            mode = "custom" if "xregpairs" in features else "native-p"
            record(
                name + "-" + mode,
                [
                    args.bin / "pattern-gen",
                    cdsl,
                    "--riscv-xlen=32",
                    "--skip-formats",
                    "--skip-verify",
                    "--mattr=" + features,
                    "-p",
                    "HasStdExtXRegPairs,IsRV32",
                    "-o",
                    output / f"{name}-{mode}.td",
                ],
            )
    loop = Path(__file__).resolve().parent / "feasibility/loops.c"
    for name, arch, extra in (
        ("custom", "rv32imxregpairs", []),
        ("native-p", "rv32imp0p21", ["-menable-experimental-extensions"]),
    ):
        command = [
            args.bin / "clang",
            "--target=riscv32",
            "-march=" + arch,
            *extra,
            "-O3",
            "-Rpass=loop-vectorize",
            "-Rpass-missed=loop-vectorize",
            "-S",
            loop,
        ]
        record("loops-" + name, [*command, "-o", output / f"loops-{name}.s"])
        record("loops-" + name + "-ir", [*command, "-emit-llvm", "-o", output / f"loops-{name}.ll"])
    vector = Path(__file__).resolve().parent / "feasibility/vector.ll"
    for name, features in (("custom", "+m,+xregpairs"), ("native-p", "+m,+experimental-p")):
        record(
            "vector-" + name,
            [
                args.bin / "llc",
                "-mtriple=riscv32",
                "-mattr=" + features,
                "-verify-machineinstrs",
                vector,
                "-o",
                output / f"vector-{name}.s",
            ],
        )
    record(
        "globalisel",
        [
            args.bin / "llc",
            "-mtriple=riscv32",
            "-mattr=+m,+xregpairs",
            "-global-isel=1",
            "-global-isel-abort=1",
            "-verify-machineinstrs",
            Path(__file__).resolve().parent / "tests/pair.test-intrinsic.ll",
            "-o",
            output / "globalisel.s",
        ],
    )
    (output / "results.json").write_text(json.dumps(records, indent=2) + "\n")
    print("Probe results (including unsupported GlobalISel) recorded in", output)


if __name__ == "__main__":
    main()

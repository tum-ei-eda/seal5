#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Verify normalized CDSL and its memory lowering with a built LLVM23 demo.

Run after examples/demo.py, with the same DEST:
    python examples/normalization/check_llvm23.py /tmp/seal5_llvm_demo_llvm23

Memory selection patterns are currently skipped by Seal5. These extra checks
still feed each memory instruction through the real pattern-gen parser and
verify the resulting LLVM load/store widths.
"""

import argparse
import csv
import json
from pathlib import Path
import re
import subprocess


def check(directory, config="release_assertions"):
    meta = Path(directory) / ".seal5"
    executable = meta / "build" / config / "bin" / "pattern-gen"
    inputs = meta / "temp" / "Normalization"
    outputs = meta / "temp" / "normalization_checks"
    outputs.mkdir(exist_ok=True)
    for metrics in (meta / "temp").glob("Normalization*metrics.csv"):
        with metrics.open() as stream:
            for row in csv.DictReader(stream):
                for key in ("n_failed", "n_failed_sets", "n_failed_instructions"):
                    if int(row.get(key) or 0):
                        raise AssertionError(f"{metrics}: {key}={row[key]}")
    cases = [
        ("XNormalize32", "NORM_LOAD16", "MEM16[", "load", 16, 32),
        ("XNormalize32", "NORM_LOADX", "MEMX[", "load", 32, 32),
        ("XNormalize32", "NORM_STORE16", "MEM16[", "store", 16, 32),
        ("XNormalize32", "NORM_MANUAL_LOAD8", "MEM8[", "load", 8, 32),
        ("XNormalize64", "NORM_LOAD64", "MEMX[", "load", 64, 64),
        ("XNormalize64", "NORM_MANUAL_LOAD32", "MEM32[", "load", 32, 64),
    ]
    results = []
    for extension, instruction, spelling, operation, width, xlen in cases:
        source = inputs / extension / f"{instruction}.core_desc"
        text = source.read_text()
        if spelling not in text:
            raise AssertionError(f"{source}: missing {spelling}")
        target = outputs / f"{instruction}.ll"
        command = [
            str(executable),
            str(source),
            "-o",
            str(target),
            "--riscv-xlen",
            str(xlen),
            "--mattr=+m",
            "--skip-patterns",
            "--skip-formats",
            "--skip-verify",
            "--no-extend",
        ]
        result = subprocess.run(command, capture_output=True, text=True)
        (outputs / f"{instruction}.log").write_text(result.stdout + result.stderr)
        if result.returncode:
            raise RuntimeError(f"{instruction}: pattern-gen failed ({result.returncode})\n{result.stderr}")
        ir_text = target.read_text()
        if not re.search(rf"\b{operation}\s+i{width}\b", ir_text):
            raise AssertionError(f"{target}: expected {operation} i{width}")
        pointers = re.findall(r"(%[\w.]+)\s*=\s*inttoptr\b[^\n]*", ir_text)
        if not any(
            re.search(rf"\b{operation}\s+i{width}\b[^\n]*\bptr\s+{re.escape(pointer)}\b", ir_text)
            for pointer in pointers
        ):
            raise AssertionError(f"{target}: expected {operation} i{width} through the instruction's memory address")
        results.append({"instruction": instruction, "xlen": xlen, "operation": operation, "width": width})
    for extension, instruction, spelling in [
        ("XNormalize32", "NORM_EXTRACT", " +: 8]"),
        ("XNormalize32", "NORM_EXTRACT_ASCENDING", " +: 4]"),
        ("XNormalize64", "NORM_WORDNAND", "XW["),
        ("XNormalize64", "NORM_MANUAL_WORDNOR", "XW["),
    ]:
        source = inputs / extension / f"{instruction}.core_desc"
        if spelling not in source.read_text():
            raise AssertionError(f"{source}: missing {spelling}")
        ir = inputs / extension / f"{instruction}.ll"
        if not ir.is_file():
            raise AssertionError(f"Missing generated LLVM IR: {ir}")
        if instruction == "NORM_EXTRACT":
            contents = ir.read_text()
            if "lshr i32 %rs1.v, %base" not in contents or "and i32" not in contents:
                raise AssertionError(f"{ir}: dynamic extraction must shift by the actual bit offset")
        results.append({"instruction": instruction, "normalized": spelling})
    report = outputs / "results.json"
    report.write_text(json.dumps(results, indent=2) + "\n")
    print(f"Verified {len(results)} LLVM23 normalization cases; report: {report}")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("directory", type=Path)
    parser.add_argument("--config", default="release_assertions")
    args = parser.parse_args()
    check(args.directory, args.config)


if __name__ == "__main__":
    main()

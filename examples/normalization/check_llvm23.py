#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Verify normalized CDSL and its memory lowering with a built LLVM23 demo.

Run after examples/demo.py, with the same DEST:
    python examples/normalization/check_llvm23.py /tmp/seal5_llvm_demo_llvm23

In addition to the lit selection tests, check that each memory instruction
has a generated pattern and verify its LLVM load/store width.
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
    for xlen in (32, 64):
        for name, operation in [
            ("LDX_REG", "load"), ("STX_REG", "store"),
            ("LDX_SCALE", "load"), ("STX_SCALE", "store"),
            ("LD_ADD", "load"), ("ST_XOR", "store"),
            ("LD_BOTH", "load"), ("ST_BOTH", "store"),
        ]:
            cases.append((f"XNormalize{xlen}", f"NORM_{name}_{xlen}",
                          "MEMX[", operation, xlen, xlen))
    results = []
    for extension, instruction, spelling, operation, width, xlen in cases:
        source = inputs / extension / f"{instruction}.core_desc"
        text = source.read_text()
        if spelling not in text:
            raise AssertionError(f"{source}: missing {spelling}")
        pattern = source.with_suffix(".td")
        if not pattern.is_file() or "def : Pat<" not in pattern.read_text():
            raise AssertionError(f"{pattern}: missing memory selection pattern")
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
    branch = inputs / "XNormalize32" / "NORM_BRANCH"
    source = branch.with_suffix(".core_desc").read_text()
    pattern = branch.with_suffix(".td").read_text()
    if "branch(" not in source or "[[is_branch_offs]]" not in source:
        raise AssertionError(f"{branch}: missing normalized branch or displacement attribute")
    if "isBranch = 1" not in pattern or "brcond" not in pattern:
        raise AssertionError(f"{branch}: missing conditional branch selection pattern")
    results.append({"instruction": "NORM_BRANCH", "branch": True})
    for xlen in (32, 64):
        for name in ("BAND", "BOR", "BXOR", "BNZ"):
            instruction = f"NORM_{name}_{xlen}"
            branch = inputs / f"XNormalize{xlen}" / instruction
            source = branch.with_suffix(".core_desc").read_text()
            pattern = branch.with_suffix(".td").read_text()
            if "branch(" not in source or "[[is_branch_offs]]" not in source:
                raise AssertionError(f"{branch}: missing normalized branch")
            if "isBranch = 1" not in pattern or "brcond" not in pattern:
                raise AssertionError(f"{branch}: missing branch selection pattern")
            results.append({"instruction": instruction, "xlen": xlen, "branch": True})
    for extension, instruction, operand, width, signed, destination, predicate in [
        ("XNormalize32", "NORM_BEQI5", "constant", 5, True, "displacement", "SETEQ"),
        ("XNormalize32", "NORM_BLTUI3", "limit", 3, False, "destination", "SETULT"),
        ("XNormalize32", "NORM_BNEI8", "threshold", 8, True, "target", "SETNE"),
        ("XNormalize64", "NORM_BLTI5_64", "bound", 5, True, "destination", "SETLT"),
    ]:
        branch = inputs / extension / instruction
        source = branch.with_suffix(".core_desc").read_text()
        pattern = branch.with_suffix(".td").read_text()
        sign = "s" if signed else "u"
        if f"seal5_{sign}imm{width}:${operand}" not in pattern or predicate not in pattern:
            raise AssertionError(f"{branch}: missing typed condition immediate or comparison predicate")
        if f"bb:${destination}" not in pattern:
            raise AssertionError(f"{branch}: condition immediate was confused with the destination")
        behavior = source.split("behavior:", 1)[1]
        if signed and f"(signed<{width}>)({operand})" not in behavior:
            raise AssertionError(f"{branch}: condition immediate lost its signed cast")
        results.append({"instruction": instruction, "condition_immediate": operand,
                        "width": width, "signed": signed, "destination": destination})
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

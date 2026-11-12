# SPDX-License-Identifier: Apache-2.0
"""Check rounded ALU IR against RV32 wraparound and masked normalization counts."""

import argparse
from pathlib import Path
import re
import subprocess


def word(value):
    value &= 0xFFFFFFFF
    return value - (1 << 32) if value & (1 << 31) else value


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("directory", type=Path, help="PatternGen's XCoreVAlu/XCoreVAlu directory")
    parser.add_argument("--opt", default="opt", help="LLVM opt executable from the tested build")
    args = parser.parse_args()
    samples = [
        (0, 0),
        (0x7FFFFFFF, 1),
        (0x7FFFFFFF, 0),
        (0x80000000, 0),
        (0x80000000, 0xFFFFFFFF),
        (0xFFFFFFFF, 0),
        (0xFFFFFFFF, 1),
        (1, 2),
        (0xFFFF0001, 0x8000FFFF),
        (0x55555555, 0xAAAAAAAA),
        (0x7FFFFFFF, 0x7FFFFFFF),
        (0x80000000, 0x80000000),
    ]
    controls = list(range(32)) + [32, 33, 63, 64, 0x7FFFFFFF, 0x80000000, 0x8000001F, 0xFFFFFFFF]
    pieces = ["declare void @llvm.assume(i1)"]
    checks = {}
    for name in ("ADDRN", "ADDURN", "SUBRN", "SUBURN", "ADDRNR", "ADDURNR", "SUBRNR", "SUBURNR"):
        text = (args.directory / f"SEAL5_CV_{name}.ll").read_text()
        bodies = re.findall(r"define void @impl.*?^}", text, re.M | re.S)
        if not bodies:
            raise ValueError(f"No extracted implementation functions for {name}")
        pieces.extend(re.sub(r", ![\w.]+ !\d+", "", re.sub(r" #\d+", "", body)) for body in bodies)
        register_count = name.endswith("R")
        for index, (a, b) in enumerate(samples):
            for control in controls if register_count else range(32):
                shift = control & 31
                rounding = (1 << shift) >> 1
                value = ((a - b if name.startswith("SUB") else a + b) + rounding) & 0xFFFFFFFF
                if not name.startswith(("ADDU", "SUBU")):
                    value = word(value)
                expected = word(value >> shift)
                fn = f"check_{name}_{index}_{control}"
                checks[fn] = expected
                callee = f"implSEAL5_CV_{name}"
                specialized = f"{callee}_{control}"
                extra = ""
                if not register_count:
                    if f"@{specialized}(" in text:
                        callee = specialized
                    else:
                        extra = f", i32 {control}"
                rd, rs1, rs2 = (a, b, control) if register_count else (0, a, b)
                pieces.append(
                    f"""define i32 @{fn}() {{
  %rd = alloca i32
  %rs1 = alloca i32
  %rs2 = alloca i32
  store i32 {word(rd)}, ptr %rd
  store i32 {word(rs1)}, ptr %rs1
  store i32 {word(rs2)}, ptr %rs2
  call void @{callee}(ptr %rd, ptr %rs1, ptr %rs2{extra})
  %result = load i32, ptr %rd
  ret i32 %result
}}"""
                )
    result = subprocess.run(
        [args.opt, "-S", "-passes=default<O2>", "-o", "-"],
        input="\n".join(pieces),
        text=True,
        capture_output=True,
        check=True,
    )
    failures = []
    for name, expected in checks.items():
        body = re.search(r"define [^@]*@" + name + r"\(\).*?^}", result.stdout, re.M | re.S).group()
        value = re.search(r"ret i32 (-?\d+)", body)
        if value is None or int(value.group(1)) != expected:
            failures.append((name, expected, body))
    if failures:
        raise AssertionError(f"{len(failures)} normalization mismatches: {failures[:5]}")
    print(f"PASS: {len(checks)} rounded ALU semantic cases")


if __name__ == "__main__":
    main()

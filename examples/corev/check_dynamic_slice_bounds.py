#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Validate local dynamic slice bounds against independent integer references."""
import argparse
from pathlib import Path
import random
import re
import subprocess


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--pattern-gen", required=True, type=Path)
    parser.add_argument("--opt", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args()
    args.output.mkdir(parents=True, exist_ok=True)
    fixture = Path(__file__).resolve().parent / "review/fixtures/dynamic-slice-bounds.core_desc"
    source = args.output / "slice-bounds.ll"
    subprocess.run(
        [args.pattern_gen, fixture, "--riscv-xlen=32", "--skip-patterns", "--skip-formats", "-o", source], check=True
    )
    text = source.read_text()
    rng = random.Random(16432)
    values = [0, 1, 0x7FFF8000, 0x80007FFF, 0xFFFFFFFF, 0x80000000]
    values += [rng.getrandbits(32) for _ in range(64)]
    checks = {}
    for name in ("SLICE_LOCAL_SIGNED", "SLICE_LOCAL_UNSIGNED", "SLICE_WIDE_BOUND"):
        for value in values:
            for lane in (0, 1):
                expected = (value >> (16 * lane)) & 0xFFFF
                if name == "SLICE_LOCAL_SIGNED" and expected & 0x8000:
                    expected |= 0xFFFF0000
                fn = f"check_{len(checks)}"
                checks[fn] = expected
                text += f"""\ndefine i32 @{fn}() {{
 %rd = alloca i32, align 4
 %rs1 = alloca i32, align 4
 store i32 {value}, ptr %rs1, align 4
 call void @impl{name}(ptr %rd, ptr %rs1, i32 {lane})
 %r = load i32, ptr %rd, align 4
 ret i32 %r
}}
"""
    source.write_text(text)
    folded = subprocess.check_output([args.opt, "-S", "-passes=default<O2>", source], text=True)
    (args.output / "slice-bounds-folded.ll").write_text(folded)
    for name, expected in checks.items():
        body = re.search(r"define [^@]*@" + name + r"\(\).*?^}", folded, re.M | re.S)
        result = re.search(r"ret i32 (-?\d+)", body[0]) if body else None
        if not result or int(result[1]) & 0xFFFFFFFF != expected:
            raise AssertionError((name, expected, body[0] if body else "Missing function"))
    print(f"{len(checks)} dynamic-slice semantic cases passed")


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Check extracted pair behavior with independent constant-folded reference cases."""
import argparse
from pathlib import Path
import random
import re
import subprocess


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("directory", type=Path, help="Directory containing the extracted .ll files")
    parser.add_argument("--opt", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args()
    args.output.mkdir(parents=True, exist_ok=True)
    rng = random.Random(42064)
    edges = [0, 1, 0xFFFFFFFF, 0x100000000, 0x7FFFFFFFFFFFFFFF, 0x8000000000000000, 0xFFFFFFFFFFFFFFFF]
    samples = [(a, b) for a in edges for b in edges]
    samples += [(rng.getrandbits(64), rng.getrandbits(64)) for _ in range(256)]
    pieces, checks = [], {}
    for name in (
        "PAIR_ADD64",
        "PAIR_ADD_2X32",
        "PAIR_SUB64",
        "PAIR_SUB_2X32",
        "PAIR_MUL_2X32",
        "PAIR_XOR64",
        "PAIR_AND64",
        "PAIR_SLLI64",
        "PAIR_SRLI64",
        "PAIR_SRAI64",
        "PAIR_RORI64",
    ):
        text = (args.directory / f"{name}.ll").read_text()
        body = re.search(r"define void @impl.*?^}", text, re.M | re.S)
        if not body:
            raise ValueError(f"No implementation for {name}")
        pieces.append(re.sub(r" #\d+", "", body[0]))
        immediate = name in ("PAIR_SLLI64", "PAIR_SRLI64", "PAIR_SRAI64", "PAIR_RORI64")
        cases = [(a, n) for a in edges for n in (0, 1, 31, 32, 33, 63)] if immediate else samples
        if immediate:
            cases += [(rng.getrandbits(64), rng.randrange(64)) for _ in range(256)]
        for n, (a, b) in enumerate(cases):
            if name == "PAIR_ADD64":
                expected = (a + b) & ((1 << 64) - 1)
            elif name == "PAIR_SUB64":
                expected = (a - b) & ((1 << 64) - 1)
            elif name == "PAIR_SUB_2X32":
                expected = ((a - b) & 0xFFFFFFFF) | ((((a >> 32) - (b >> 32)) & 0xFFFFFFFF) << 32)
            elif name == "PAIR_MUL_2X32":
                expected = (((a & 0xFFFFFFFF) * (b & 0xFFFFFFFF)) & 0xFFFFFFFF) | (
                    ((((a >> 32) * (b >> 32)) & 0xFFFFFFFF) << 32)
                )
            elif name == "PAIR_XOR64":
                expected = a ^ b
            elif name == "PAIR_AND64":
                expected = a & b
            elif name == "PAIR_SLLI64":
                expected = (a << b) & ((1 << 64) - 1)
            elif name == "PAIR_SRLI64":
                expected = a >> b
            elif name == "PAIR_SRAI64":
                expected = ((a - (1 << 64) if a >> 63 else a) >> b) & ((1 << 64) - 1)
            elif name == "PAIR_RORI64":
                expected = ((a >> b) | (a << ((64 - b) & 63))) & ((1 << 64) - 1)
            else:
                expected = ((a + b) & 0xFFFFFFFF) | ((((a >> 32) + (b >> 32)) & 0xFFFFFFFF) << 32)
            fn = f"check_{name}_{n}"
            checks[fn] = expected
            rhs = f"i32 {b}" if immediate else "ptr %b"
            pieces.append(
                f"""define i64 @{fn}() {{
 %rd = alloca i64, align 8
 %a = alloca i64, align 8
 %b = alloca i64, align 8
 store i64 {a}, ptr %a, align 8
 store i64 {b}, ptr %b, align 8
 call void @impl{name}(ptr %rd, ptr %a, {rhs})
 %r = load i64, ptr %rd, align 8
 ret i64 %r
}}"""
            )
    source = args.output / "semantics.ll"
    source.write_text("\n".join(pieces))
    result = subprocess.run([args.opt, "-S", "-passes=default<O2>", source], check=True, capture_output=True, text=True)
    (args.output / "semantics-folded.ll").write_text(result.stdout)
    for name, expected in checks.items():
        body = re.search(r"define [^@]*@" + name + r"\(\).*?^}", result.stdout, re.M | re.S)[0]
        value = re.search(r"ret i64 (-?\d+)", body)
        if not value or int(value[1]) & ((1 << 64) - 1) != expected:
            raise AssertionError((name, expected, body))
    print(f"{len(checks)} pair semantic cases passed")


if __name__ == "__main__":
    main()

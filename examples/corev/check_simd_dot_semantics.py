# SPDX-License-Identifier: Apache-2.0
"""Check extracted packed dot-product rules against independent lane arithmetic."""

import argparse
from pathlib import Path
import random
import re

from check_simd_comparison_semantics import WORD_MASK, evaluate, parse_pattern, signed


def reference(name, a, b, accumulator):
    accumulate, kind, broadcast, width = re.fullmatch(r"SEAL5_CV_(S?)DOT(SP|UP|USP)(?:_(SC))?_([BH])", name).groups()
    bits = 8 if width == "B" else 16
    mask = (1 << bits) - 1
    result = accumulator if accumulate else 0
    for offset in range(0, 32, bits):
        left = (a >> offset) & mask
        right = (b >> (0 if broadcast else offset)) & mask
        if kind == "SP":
            left = signed(left, bits)
        if kind != "UP":
            right = signed(right, bits)
        result += left * right
    return result & WORD_MASK


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("directory", type=Path, help="Directory containing PatternGen .td.out logs")
    args = parser.parse_args()
    boundaries = [0, 1, 0x7F, 0x80, 0xFF, 0x7FFF, 0x8000, 0xFFFF,
                  0x7F80FF00, 0x807F00FF, 0x7FFF8000, 0x80007FFF, WORD_MASK]
    rng = random.Random(0)
    samples = [(a, b, c) for a in boundaries for b in boundaries for c in (0, 0x7FFFFFFF, 0x80000000, WORD_MASK)]
    samples += [(rng.getrandbits(32), rng.getrandbits(32), rng.getrandbits(32)) for _ in range(1024)]
    seen = set()
    checks = rules = 0
    for path in sorted(args.directory.glob("SEAL5_CV_*DOT*.td.out")):
        for name, text in re.findall(r"^Pattern for (\S+) \[[^\]]+\]: (.+)$", path.read_text(), re.M):
            if "_SCI_" in name:
                continue
            tree = parse_pattern(text)
            seen.add(name)
            rules += 1
            for a, b, accumulator in samples:
                actual = evaluate(tree, {"rs1": a, "rs2": b, "rd": accumulator})
                expected = reference(name, a, b, accumulator)
                assert actual == expected, (name, hex(a), hex(b), hex(accumulator), hex(actual), hex(expected))
                checks += 1
    assert len(seen) == 24, f"Expected all 24 register/broadcast instructions, found {len(seen)}"
    print(f"{checks:,} checks across {rules} rules / {len(seen)} dot-product instructions")


if __name__ == "__main__":
    main()

# SPDX-License-Identifier: Apache-2.0
"""Check extracted clip IR against CORE-V bounds, including negative bound registers."""

import argparse
from pathlib import Path
import re
import subprocess
from tempfile import TemporaryDirectory


def signed(value):
    """Interpret a word as a signed RV32 value."""
    value &= 0xFFFFFFFF
    return value - (1 << 32) if value & (1 << 31) else value


def check_pattern_variants(directory, pattern_gen):
    """Require the bounds proof before emitting interchangeable clamp orders."""
    with TemporaryDirectory() as temporary:
        root = Path(temporary)
        for name, known_count in (("CLIPR", 2), ("CLIPUR", 3)):
            original = (directory / f"SEAL5_CV_{name}.core_desc").read_text()
            masked_bound = "(unsigned<31>)(X[rs2][(30):(0)])"
            if masked_bound not in original:
                raise ValueError(f"Missing masked bound in {name}")
            for known in (True, False):
                source = root / f"{name}_{known}.core_desc"
                source.write_text(original if known else original.replace(masked_bound, "(signed<32>)(X[rs2])"))
                result = subprocess.run(
                    [
                        str(pattern_gen),
                        str(source),
                        "-o",
                        str(root / "patterns.td"),
                        "--mattr=+m,+seal5-minmax32",
                        "--riscv-xlen=32",
                        "--skip-formats",
                        "--skip-verify",
                    ],
                    capture_output=True,
                    text=True,
                    check=True,
                )
                count = len(re.findall(r"^Pattern for ", result.stdout, re.M))
                expected = known_count if known else 1
                if count != expected:
                    raise AssertionError(
                        f"{name} known={known}: expected {expected} rules, got {count}\n{result.stderr}"
                    )
        source = root / "CLIPU.core_desc"
        source.write_text((directory / "SEAL5_CV_CLIPU.core_desc").read_text())
        result = subprocess.run(
            [
                str(pattern_gen),
                str(source),
                "-o",
                str(root / "constant-skips.td"),
                "--mattr=+m,+seal5-minmax32",
                "--riscv-xlen=32",
                "--skip-formats",
                "--skip-verify",
            ],
            capture_output=True,
            text=True,
            check=True,
        )
        skipped = re.findall(r"^Skipped constant specialization for (\S+)", result.stdout, re.M)
        matched = set(re.findall(r"^Pattern for (\S+)", result.stdout, re.M))
        if set(skipped) != {"SEAL5_CV_CLIPU_0", "SEAL5_CV_CLIPU_1"} or len(matched) != 30:
            raise AssertionError(f"Unexpected unsigned clip specializations: {skipped}, {matched}")
    print("PASS: 4 clamp bounds-proof checks and 2 constant-specialization skips")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("directory", type=Path, help="PatternGen's XCoreVAlu/XCoreVAlu output directory")
    parser.add_argument("--opt", default="opt", help="LLVM opt executable from the tested build")
    parser.add_argument("--pattern-gen", type=Path, help="Also check equivalent-pattern bounds proofs")
    args = parser.parse_args()
    if args.pattern_gen:
        check_pattern_variants(args.directory, args.pattern_gen)
    pieces = [
        "declare void @llvm.assume(i1)",
        "declare i32 @llvm.smin.i32(i32, i32)",
        "declare i32 @llvm.smax.i32(i32, i32)",
        "declare i32 @llvm.umin.i32(i32, i32)",
    ]
    checks = {}
    for name in ("CLIP", "CLIPU", "CLIPR", "CLIPUR"):
        text = (args.directory / f"SEAL5_CV_{name}.ll").read_text()
        bodies = re.findall(r"define void @impl.*?^}", text, re.M | re.S)
        if not bodies:
            raise ValueError(f"No extracted implementations for {name}")
        pieces.extend(re.sub(r", ![\w.]+ !\d+", "", re.sub(r" #\d+", "", body)) for body in bodies)
        register_bound = name.endswith("R")
        bounds = (
            [0, 1, 2, 63, 0x3FFFFFFF, 0x7FFFFFFF, 0x80000000, 0x8000003F, 0xFFFFFFFF] if register_bound else range(32)
        )
        for bound in bounds:
            upper = (bound & 0x7FFFFFFF) if register_bound else (1 << max(0, bound - 1)) - 1
            lower = 0 if "U" in name else -upper - 1
            values = {-(1 << 31), -1, 0, 1, (1 << 31) - 1}
            values.update(signed(v) for v in (lower - 1, lower, lower + 1, upper - 1, upper, upper + 1))
            for index, value in enumerate(sorted(values)):
                fn = f"check_{name}_{bound}_{index}"
                checks[fn] = min(max(value, lower), upper)
                callee = f"implSEAL5_CV_{name}"
                if f"@{callee}_{bound}(" in text:
                    callee += f"_{bound}"
                    extra = ""
                else:
                    extra = ", ptr %bound" if register_bound else f", i32 {bound}"
                pieces.append(
                    f"""define i32 @{fn}() {{
  %rd = alloca i32
  %input = alloca i32
  %bound = alloca i32
  store i32 {value}, ptr %input
  store i32 {signed(bound)}, ptr %bound
  call void @{callee}(ptr %rd, ptr %input{extra})
  %v = load i32, ptr %rd
  ret i32 %v
}}"""
                )
    result = subprocess.run(
        [args.opt, "-S", "-passes=default<O2>", "-o", "-"],
        input="\n".join(pieces),
        capture_output=True,
        text=True,
        check=True,
    )
    failures = []
    for name, expected in checks.items():
        body = re.search(r"define [^@]*@" + name + r"\(\).*?^}", result.stdout, re.M | re.S).group()
        value = re.search(r"ret i32 (-?\d+)", body)
        if value is None or int(value.group(1)) != expected:
            failures.append((name, expected, body))
    if failures:
        raise AssertionError(f"{len(failures)} clip semantic mismatches: {failures[:5]}")
    print(f"PASS: {len(checks)} clip semantic cases")


if __name__ == "__main__":
    main()

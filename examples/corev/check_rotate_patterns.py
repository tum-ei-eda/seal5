#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Check that rotate identity variants require the matching guard and value."""
import argparse
from pathlib import Path
import re
import subprocess
from tempfile import TemporaryDirectory


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("directory", type=Path)
    parser.add_argument("--pattern-gen", required=True, type=Path)
    args = parser.parse_args()
    source = (args.directory / "SEAL5_CV_ROR.core_desc").read_text()
    cases = (
        ("valid", source, 2),
        ("wrong_guard", source.replace("(shift) == (0)", "(shift) == (1)"), 1),
        ("wrong_value", source.replace("X[rd] = X[rs1];", "X[rd] = X[rs2];"), None),
    )
    with TemporaryDirectory() as temporary:
        root = Path(temporary)
        for name, text, expected in cases:
            path = root / f"{name}.core_desc"
            path.write_text(text)
            result = subprocess.run(
                [
                    str(args.pattern_gen),
                    str(path),
                    "-o",
                    str(root / "patterns.td"),
                    "--mattr=+m,+seal5-rotate32",
                    "--riscv-xlen=32",
                    "--skip-formats",
                    "--skip-verify",
                ],
                capture_output=True,
                text=True,
            )
            patterns = re.findall(r"^Pattern for .*: (.*)$", result.stdout, re.M)
            if expected is not None:
                assert result.returncode == 0 and len(patterns) == expected, (name, result.stderr, patterns)
            else:
                # An unsupported negative case may be rejected entirely; it must never
                # introduce an unconditional rotate that discards the changed value.
                assert all("select" in pattern for pattern in patterns), (name, patterns)
            print(f"{name}: PASS ({len(patterns)} patterns)")


if __name__ == "__main__":
    main()

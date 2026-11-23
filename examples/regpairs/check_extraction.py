#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Check pair extraction, including arithmetic expressions that must not match."""
import argparse
import json
from pathlib import Path
import subprocess


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("directory", type=Path, help="Directory containing reduced pair .core_desc files")
    parser.add_argument("--pattern-gen", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args()
    args.output.mkdir(parents=True, exist_ok=True)
    records = []

    def check(name, text, expected):
        source = args.output / (name + ".core_desc")
        source.write_text(text)
        output = source.with_suffix(".td")
        command = [
            str(args.pattern_gen),
            str(source),
            "--riscv-xlen=32",
            "--skip-formats",
            "--skip-verify",
            "--mattr=+m,+xregpairs",
            "-p",
            "HasStdExtXRegPairs,IsRV32",
            "-o",
            str(output),
        ]
        result = subprocess.run(command, capture_output=True, text=True, timeout=60)
        source.with_suffix(".stdout").write_text(result.stdout)
        source.with_suffix(".stderr").write_text(result.stderr)
        records.append({"name": name, "command": command, "exit_code": result.returncode, "expected_success": expected})
        (args.output / "results.json").write_text(json.dumps(records, indent=2) + "\n")
        if result.returncode < 0 or (result.returncode == 0) != expected:
            raise AssertionError((name, result.returncode, result.stderr))
        if expected and "def : Pat<" not in output.read_text():
            raise AssertionError("Missing pattern: " + name)
        if not expected and output.exists() and "def : Pat<" in output.read_text():
            raise AssertionError("Unexpected partial pattern: " + name)

    sources = {p.stem: p.read_text() for p in args.directory.rglob("*.core_desc")}
    for name, text in sorted(sources.items()):
        check(name, text, True)
    for name, old, new in (
        ("PAIR_SUB_2X32", "b[(63):(32)]", "a[(63):(32)]"),
        ("PAIR_MUL_2X32", "b[(63):(32)]", "a[(63):(32)]"),
    ):
        text = sources[name]
        assert text.count(old) == 1, (name, old)
        check(name + "_mismatched_inputs", text.replace(old, new), False)
    text = sources["PAIR_SUB_2X32"]
    old = "(a[(63):(32)]) - (b[(63):(32)])"
    assert text.count(old) == 1
    check("PAIR_SUB_2X32_reversed_high", text.replace(old, "(b[(63):(32)]) - (a[(63):(32)])"), False)
    print(f"{len(records)} pair extraction checks passed")


if __name__ == "__main__":
    main()

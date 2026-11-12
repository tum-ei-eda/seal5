#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Prepare and validate ordinary TableGen packed-SIMD patterns (RV32)."""

import argparse
import re
from pathlib import Path
import subprocess

FIXTURES = Path(__file__).resolve().parent / "fixtures"


def run(command, source=None):
    result = subprocess.run(list(map(str, command)), input=source, capture_output=True, text=True)
    if result.returncode:
        raise RuntimeError(f"{command}\n{result.stdout}\n{result.stderr}")
    return result.stdout


def prepare(binary, output):
    definitions, formats = [], []
    for source in sorted(FIXTURES.glob("*.core_desc")):
        name = source.stem.upper()
        lanes, bits = map(int, name.rsplit("_", 1)[1].split("X"))
        target = output / source.with_suffix(".td").name
        log = run(
            [
                binary / "pattern-gen",
                source,
                "--no-extend",
                "--riscv-xlen=32",
                "--mattr=+m,+gpr32v",
                "-p",
                "HasGPR32V,IsRV32",
                "-o",
                target,
            ]
        )
        (output / f"{source.stem}.log").write_text(log)
        contents = target.read_text()
        assert f"v{lanes}i{bits}" in contents, contents
        assert contents.count("def : Pat<") == 1, contents
        assert not target.with_suffix(".inc").exists(), "Direct matcher output is outside this example's scope"
        # Standalone fixture definitions are decoder-visible for roundtrip tests.
        contents = contents.replace("isCodeGenOnly = 1", "isCodeGenOnly = 0")
        contents = contents.replace("def : Pat<", "let AddedComplexity = 1000 in def : Pat<")
        target.write_text(contents)
        definitions.append(f'include "{target}"')
        formats.append(f'include "{target.with_name(target.stem + "InstrFormat.td")}"')
    (output / "patterns.td").write_text("\n".join(definitions) + "\n")
    (output / "formats.td").write_text("\n".join(formats) + "\n")
    print("Prepared four ordinary vector-typed TableGen patterns in", output)


def check(binary, output, extension=None):
    enabled = "+m,+gpr32v" + (f",+{extension}" if extension else ",+gpr32v-add,+gpr32v-sub")
    disabled_vectors = "+m,-gpr32v" + (f",+{extension}" if extension else "")
    for source in sorted(FIXTURES.glob("*.ll")):
        name = source.stem.upper()
        mnemonic = "pack." + source.stem.removeprefix("pack_").replace("_", ".")
        ir = source.read_text()
        for level in (0, 2, 3):
            for selector in ("globalisel", "selectiondag"):
                command = [
                    binary / "llc",
                    "-mtriple=riscv32",
                    f"-O{level}",
                    f"-mattr={enabled}",
                    "-verify-machineinstrs",
                ]
                command += (
                    ["-global-isel=1", "-global-isel-abort=1"] if selector == "globalisel" else ["-global-isel=0"]
                )
                asm = run(command, ir)
                assert mnemonic in asm, asm
                if name.startswith("PACK_SUB") and level >= 2:
                    assert re.search(re.escape(mnemonic) + r"\s+a0, a0, a1", asm), asm
                (output / f"{source.stem}-{selector}-O{level}.s").write_text(asm)
                obj = output / f"{source.stem}-{selector}-O{level}.o"
                run([*command, "-filetype=obj", "-o", obj], ir)
                decoded = run([binary / "llvm-objdump", "-d", f"--mattr={enabled}", obj])
                assert mnemonic in decoded and "<unknown>" not in decoded, decoded
        lanes, bits = map(int, name.rsplit("_", 1)[1].split("X"))
        operation = "sub" if "SUB" in name else "add"
        for alignment in (1, 4):
            memory_ir = f"""define void @memory(ptr %a, ptr %b, ptr %out) {{
  %x = load <{lanes} x i{bits}>, ptr %a, align {alignment}
  %y = load <{lanes} x i{bits}>, ptr %b, align {alignment}
  %z = {operation} <{lanes} x i{bits}> %x, %y
  store <{lanes} x i{bits}> %z, ptr %out, align {alignment}
  ret void
}}
"""
            for selector in (0, 1):
                asm = run(
                    [
                        binary / "llc",
                        "-mtriple=riscv32",
                        "-O2",
                        f"-mattr={enabled}",
                        f"-global-isel={selector}",
                        "-global-isel-abort=1",
                        "-verify-machineinstrs",
                    ],
                    memory_ir,
                )
                assert mnemonic in asm, asm
                (output / f"{source.stem}-memory-align{alignment}-isel{selector}.s").write_text(asm)
        # Native SelectionDAG can scalarize explicit vector IR when disabled.
        native = run(
            [
                binary / "llc",
                "-mtriple=riscv32",
                "-O2",
                f"-mattr={disabled_vectors}",
                "-global-isel=0",
                "-verify-machineinstrs",
            ],
            ir,
        )
        assert "pack." not in native, native
        obj = output / f"{source.stem}-globalisel-O2.o"
        disabled = run([binary / "llvm-objdump", "-d", f"--mattr=-{extension or 'gpr32v'}", obj])
        assert mnemonic not in disabled, disabled
        print(
            name,
            "selected at O0/O2/O3 with both selectors; aligned/unaligned transfers, decoding and feature gating passed",
        )


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("binary", type=Path)
    parser.add_argument("action", choices=("prepare", "check"))
    parser.add_argument("output", type=Path)
    parser.add_argument("--extension", help="ISA feature required by a Seal5-generated backend")
    args = parser.parse_args()
    args.output = args.output.resolve()
    args.output.mkdir(parents=True, exist_ok=True)
    if args.action == "prepare":
        prepare(args.binary.resolve(), args.output)
    else:
        check(args.binary.resolve(), args.output, args.extension)


if __name__ == "__main__":
    main()

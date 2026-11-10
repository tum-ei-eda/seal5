#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Exercise a GNU build patched using Seal5's Example and XCoreVNand models."""

import argparse
import subprocess
import tempfile
from pathlib import Path


ASSEMBLY = """.attribute arch, "rv32i2p1_xcorevnand1p0_xexample1p0"
.text
.global _start
_start:
 cv.nand.bitwise a0, a1, a2
 xexample.subincacc a0, a1, a2
 xexample.slli_add_addi a0, a1, a2, -4, 31
 jal ra, custom_target
"""
EXPECTED = ("cv.nand.bitwise", "xexample.subincacc", "xexample.slli_add_addi")


def run(*command, text=None, success=True):
    """Check exit status and retain output for a useful failure report."""
    result = subprocess.run([str(part) for part in command], input=text, text=True, capture_output=True, check=False)
    if (result.returncode == 0) != success:
        raise RuntimeError(f"Unexpected status {result.returncode}: {command}\n{result.stdout}{result.stderr}")
    return result.stdout + result.stderr


def check_mnemonics(output):
    """Require custom names, not fallback raw instruction words."""
    for mnemonic in EXPECTED:
        if mnemonic not in output:
            raise RuntimeError(f"Missing {mnemonic} in:\n{output}")


def main():
    """Run demo assembly, linking and disassembly assertions."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--build", type=Path, required=True, help="GNU build directory")
    parser.add_argument("--gdb", type=Path, help="Optional GDB executable (may be in a separate build)")
    parser.add_argument("--llvm-demo", type=Path, help="Optional Seal5 demo directory for LLVM object checks")
    args = parser.parse_args()
    assembler = args.build / "gas/as-new"
    linker = args.build / "ld/ld-new"
    objdump = args.build / "binutils/objdump"
    readelf = args.build / "binutils/readelf"
    with tempfile.TemporaryDirectory(prefix="seal5-gnu-test-") as directory:
        root = Path(directory)
        obj, elf = root / "custom.o", root / "custom.elf"
        run(assembler, "-march=rv32i_xcorevnand_xexample", "-o", obj, text=ASSEMBLY)
        decoded = run(objdump, "-d", obj)
        check_mnemonics(decoded)
        for word in ("92c5e52b", "50c5b52b", "9f62d457"):
            if word not in decoded:
                raise RuntimeError(f"Incorrect encoding, missing {word}:\n{decoded}")
        for immediate in (-4, -1, 0, 3):
            run(
                assembler,
                "-march=rv32i_xexample",
                "-o",
                root / "boundary.o",
                text=f"xexample.slli_add_addi a0,a1,a2,{immediate},31\n",
            )
        for operands in ("a0,a1,a2,-5,0", "a0,a1,a2,4,0", "a0,a1,a2,0,-1", "a0,a1,a2,0,32"):
            run(
                assembler,
                "-march=rv32i_xexample",
                "-o",
                root / "invalid.o",
                text=f"xexample.slli_add_addi {operands}\n",
                success=False,
            )
        run(assembler, "-march=rv32i", "-o", root / "disabled.o", text="xexample.subincacc a0,a1,a2\n", success=False)
        helper = root / "helper.o"
        run(
            assembler,
            "-march=rv32i_xexample",
            "-o",
            helper,
            text=".text\n.global custom_target\ncustom_target:\n xexample.subincacc a0,a1,a2\n",
        )
        relocations = run(readelf, "-r", obj)
        if "R_RISCV_JAL" not in relocations or "custom_target" not in relocations:
            raise RuntimeError(f"Missing cross-object relocation:\n{relocations}")
        run(linker, "-m", "elf32lriscv", "-e", "_start", "-Ttext=0x1000", "-o", elf, obj, helper)
        check_mnemonics(run(objdump, "-d", elf))
        if args.gdb:
            check_mnemonics(run(args.gdb, "-nx", "-batch", elf, "-ex", "disassemble /r _start,_start+12"))
        if args.llvm_demo:
            outputs = args.llvm_demo / ".seal5/tests/Output"
            linked = root / "llvm-linked.o"
            run(
                linker,
                "-m",
                "elf32lriscv",
                "-r",
                "-o",
                linked,
                outputs / "cv-nand-bitwise.test-inline-asm.c.tmp.o",
                outputs / "xexample-subincacc.test-inline-asm.c.tmp.o",
            )
            attributes = run(readelf, "-A", linked)
            for extension in ("xcorevnand1p0", "xexample1p0"):
                if extension not in attributes:
                    raise RuntimeError(f"Missing merged extension {extension}:\n{attributes}")
            decoded = run(objdump, "-d", linked)
            for mnemonic in EXPECTED[:2]:
                if mnemonic not in decoded:
                    raise RuntimeError(f"LLVM object missing {mnemonic}:\n{decoded}")
            if args.gdb:
                decoded = run(args.gdb, "-nx", "-batch", linked, "-ex", "disassemble /r test_nand,test_nand+4")
                if "cv.nand.bitwise" not in decoded:
                    raise RuntimeError(f"GDB did not decode LLVM output:\n{decoded}")
    print("GNU demo checks passed: encodings, immediate ranges, extension gating, linking and decoding")


if __name__ == "__main__":
    main()

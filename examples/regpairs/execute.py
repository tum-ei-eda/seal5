#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Execute builtin/intrinsic pair code with an independent RV32 Spike model."""
import argparse
import json
from pathlib import Path
import subprocess

ROOT = Path(__file__).resolve().parent
COMMON = ROOT.parent / "packed_simd/runtime"


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    for name in ("bin", "gcc", "spike", "spike-source", "spike-build", "output"):
        parser.add_argument("--" + name, required=True, type=Path)
    args = parser.parse_args()
    args.output.mkdir(parents=True, exist_ok=True)
    output = args.output.resolve()
    records = []

    def run(name, command):
        result = subprocess.run(list(map(str, command)), capture_output=True, text=True, timeout=120)
        (output / f"{name}.stdout").write_text(result.stdout)
        (output / f"{name}.stderr").write_text(result.stderr)
        records.append({"name": name, "command": list(map(str, command)), "exit_code": result.returncode})
        (output / "results.json").write_text(json.dumps(records, indent=2) + "\n")
        if result.returncode:
            raise RuntimeError(f"{name} failed; see {output / (name + '.stderr')}")
        return result.stdout

    plugin = output / "libseal5-regpairs.so"
    run(
        "plugin",
        [
            "c++",
            "-std=c++17",
            "-fPIC",
            "-shared",
            f"-I{args.spike_source / 'riscv'}",
            f"-I{args.spike_source}",
            f"-I{args.spike_build}",
            ROOT / "runtime/spike.cc",
            "-o",
            plugin,
        ],
    )
    gcc = [args.gcc, "-march=rv32im", "-mabi=ilp32", "-O2"]
    reference = output / "reference.o"
    run("reference", [*gcc, "-c", ROOT / "runtime/check.c", "-o", reference])
    bit_reference = output / "reference-bitops.o"
    run("reference-bitops", [*gcc, "-c", ROOT / "runtime/check_bitops.c", "-o", bit_reference])
    for level in (0, 2, 3):
        objects = []
        clang = [
            args.bin / "clang",
            "--target=riscv32",
            "-march=rv32imxregpairs",
            "-mabi=ilp32",
            f"-O{level}",
            "-mllvm",
            "-verify-machineinstrs",
        ]
        for name, source in (
            ("builtins", ROOT / "tests/pair.test-builtin.c"),
            ("bitops", ROOT / "tests/pair.test-bitops.c"),
            ("intrinsics", ROOT / "tests/pair.test-intrinsic.ll"),
            ("stress", ROOT / "runtime/stress.c"),
            ("automatic", ROOT / "runtime/automatic.c"),
            ("alias", ROOT / "runtime/alias.S"),
        ):
            # The intrinsic file also defines add64/add_2x32. Rename its two
            # direct wrappers, leaving unaligned_abi for the execution test.
            if name == "intrinsics":
                target = output / "intrinsics.ll"
                text = source.read_text()
                for wrapper in ("add64", "add_2x32", "sub64", "sub_2x32", "mul_2x32"):
                    text = text.replace("@" + wrapper + "(", "@ir_" + wrapper + "(")
                target.write_text(text)
                source = target
            obj = output / f"{name}-O{level}.o"
            run(f"{name}-O{level}", [*clang, "-c", source, "-o", obj])
            # Decode linker-removable two-byte alignment padding as c.nop.
            decoded = run(
                f"{name}-O{level}-disassembly",
                [args.bin / "llvm-objdump", "-d", "--mattr=+xregpairs,+c", "--disassembler-options=numeric", obj],
            )
            expected = ["pair.add64", "pair.add.2x32", "pair.sub64", "pair.sub.2x32", "pair.mul.2x32"]
            if name == "bitops":
                expected = ["pair.xor64", "pair.and64", "pair.slli64", "pair.srli64", "pair.srai64", "pair.rori64"]
            if name == "stress":
                expected = ["pair.add64"]
            if "<unknown>" in decoded or any(mnemonic not in decoded for mnemonic in expected):
                raise AssertionError(f"Missing or undecodable pair instruction in {obj}")
            objects.append(obj)
        elf = output / f"check-O{level}.elf"
        run(
            f"link-O{level}",
            [
                *gcc,
                "-nostdlib",
                f"-Wl,-T,{COMMON / 'link.ld'}",
                COMMON / "start.S",
                reference,
                bit_reference,
                *objects,
                "-lgcc",
                "-o",
                elf,
            ],
        )
        run(
            f"execute-O{level}",
            [args.spike, "--isa=RV32IM", "-m128", f"--extlib={plugin}", "--extension=seal5_regpairs", elf],
        )
    print("RV32 pair code passed at O0/O2/O3: boundaries, random arithmetic, odd ABI alignment, spills, overlap and x0")


if __name__ == "__main__":
    main()

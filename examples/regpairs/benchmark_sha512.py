#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Compare unchanged Mbed TLS 2.28.10 SHA-512 compression on RV32 under Spike.

Supply library/sha512.c from the mbedtls-2.28.10 tag. Only dependencies are
shimmed; the compression function and round constants are extracted unchanged.
The measurement counts retired instructions, not hardware cycles.
"""
import argparse
import hashlib
import json
from pathlib import Path
import re
import subprocess

ROOT = Path(__file__).resolve().parent


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    for name in ("bin", "gcc", "spike", "pair-plugin", "marker-plugin", "source", "output"):
        parser.add_argument("--" + name, required=True, type=Path)
    args = parser.parse_args()
    args.output.mkdir(parents=True, exist_ok=True)
    output = args.output.resolve()
    upstream = args.source.read_text()
    start = upstream.index("static const uint64_t K[80]")
    end = upstream.index("\n#if !defined(MBEDTLS_DEPRECATED_REMOVED)", start)
    kernel = output / "sha512-kernel.c"
    kernel.write_text((ROOT / "benchmark/sha512-shim.h").read_text() + upstream[start:end])
    records = []
    compiler_version = subprocess.check_output([args.bin / "clang", "--version"], text=True).splitlines()[0]

    def run(label, command):
        command = list(map(str, command))
        result = subprocess.run(command, capture_output=True, text=True, timeout=120)
        (output / (label + ".stdout")).write_text(result.stdout)
        (output / (label + ".stderr")).write_text(result.stderr)
        if result.returncode:
            raise RuntimeError(f"{label} failed: {result.stderr[-2000:]}")
        return result.stdout, result.stderr

    for smaller in (False, True):
        for level in (2, 3):
            for mode in ("baseline", "add-only", "full"):
                label = f'{"small" if smaller else "default"}-O{level}-{mode}'
                obj, elf = output / (label + ".o"), output / (label + ".elf")
                flags = []
                if mode == "add-only":
                    flags += ["-mllvm", "-riscv-seal5-regpair-bitops=false"]
                if smaller:
                    flags += ["-DMBEDTLS_SHA512_SMALLER"]
                run(
                    label + "-compile",
                    [
                        args.bin / "clang",
                        "--target=riscv32",
                        "-march=rv32im" + ("xregpairs" if mode != "baseline" else ""),
                        "-mabi=ilp32",
                        f"-O{level}",
                        "-ffreestanding",
                        "-ffunction-sections",
                        "-fdata-sections",
                        "-isystem",
                        args.gcc.parent.parent / "riscv64-unknown-elf/include",
                        *flags,
                        "-c",
                        kernel,
                        "-o",
                        obj,
                    ],
                )
                assembly, _ = run(label + "-disassembly", [args.bin / "llvm-objdump", "-d", "--mattr=+xregpairs", obj])
                runtime = ROOT.parent / "packed_simd/runtime"
                run(
                    label + "-link",
                    [
                        args.gcc,
                        "-march=rv32im_zicsr_zicntr",
                        "-mabi=ilp32",
                        "-O2",
                        "-nostartfiles",
                        f'-Wl,-T,{runtime / "link.ld"}',
                        "-Wl,--gc-sections",
                        runtime / "start.S",
                        ROOT / "benchmark/sha512-main.c",
                        obj,
                        "-lm",
                        "-lc",
                        "-lgcc",
                        "-lnosys",
                        "-o",
                        elf,
                    ],
                )
                _, stderr = run(
                    label + "-execute",
                    [
                        args.spike,
                        "--isa=RV32IM_Zicsr_Zicntr",
                        "-m128",
                        "--extlib=" + str(args.marker_plugin),
                        "--extlib=" + str(args.pair_plugin),
                        "--extension=seal5_packed",
                        "--extension=seal5_regpairs",
                        elf,
                    ],
                )
                measurement = json.loads(re.search(r"SEAL5_MEASURE (\{.*\})", stderr)[1])
                record = dict(
                    label=label, **measurement, static_pair_instructions=len(re.findall(r"\bpair\.", assembly))
                )
                if (record["static_pair_instructions"] > 0) != (mode != "baseline"):
                    raise AssertionError(f"{label}: unexpected instruction selection")
                if mode == "add-only" and re.search(r"pair\.(?:xor64|and64|slli64|srli64|srai64|rori64)", assembly):
                    raise AssertionError(f"{label}: new bit operations were selected")
                record["pair_instruction_counts"] = {
                    op: len(re.findall(r"\bpair\." + re.escape(op) + r"\b", assembly))
                    for op in ("add64", "xor64", "and64", "slli64", "srli64", "srai64", "rori64")
                }
                records.append(record)
                (output / "results.json").write_text(
                    json.dumps(
                        dict(
                            compiler_version=compiler_version,
                            source_sha256=hashlib.sha256(args.source.read_bytes()).hexdigest(),
                            records=records,
                        ),
                        indent=2,
                    )
                    + "\n"
                )
                print(record, flush=True)


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Measure and optionally profile unchanged Embench aha-mont64 with RV32 pairs."""
import argparse
import collections
import hashlib
import json
from pathlib import Path
import re
import subprocess

ROOT = Path(__file__).resolve().parent


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    for name in ("embench-root", "bin", "gcc", "spike", "pair-plugin", "marker-plugin", "output"):
        parser.add_argument("--" + name, required=True, type=Path)
    parser.add_argument("--profile", action="store_true", help="Collect whole-run PC histograms, including warmup")
    args = parser.parse_args()
    args.output.mkdir(parents=True, exist_ok=True)
    output = args.output.resolve()
    source = args.embench_root / "src/aha-mont64/mont64.c"
    support = args.embench_root / "support"
    runtime = ROOT.parent / "packed_simd/runtime"
    records = []

    def run(label, command, stdin=None):
        command = list(map(str, command))
        result = subprocess.run(command, input=stdin, capture_output=True, text=True, timeout=120)
        (output / (label + ".command.json")).write_text(json.dumps(command) + "\n")
        (output / (label + ".stdout")).write_text(result.stdout)
        (output / (label + ".stderr")).write_text(result.stderr)
        if result.returncode:
            raise RuntimeError(f"{label} failed: {result.stderr[-2000:]}")
        return result.stdout, result.stderr

    def profile(label, elf, stderr):
        pcs = {
            int(pc, 16) & 0xFFFFFFFF: int(count) for pc, count in re.findall(r"^([0-9a-f]{8,16}) (\d+)$", stderr, re.M)
        }
        addr2line = args.gcc.with_name(args.gcc.name.removesuffix("gcc") + "addr2line")
        text, _ = run(
            label + "-source-profile", [addr2line, "-a", "-f", "-i", "-e", elf], "\n".join(hex(pc) for pc in pcs) + "\n"
        )
        frames, pc, entry = {}, None, []
        for line in text.splitlines():
            if re.fullmatch(r"0x[0-9a-f]+", line):
                if pc is not None:
                    frames[pc] = list(zip(entry[::2], entry[1::2]))
                pc, entry = int(line, 16), []
            else:
                entry.append(line)
        if pc is not None:
            frames[pc] = list(zip(entry[::2], entry[1::2]))
        dis, _ = run(label + "-linked-disassembly", [args.bin / "llvm-objdump", "-d", "--mattr=+xregpairs", elf])
        opcodes = {int(pc, 16): op for pc, op in re.findall(r"^\s*([0-9a-f]+):\s+[0-9a-f]{8}\s+(\S+)", dis, re.M)}
        functions, body_ops = collections.Counter(), collections.Counter()
        for pc, count in pcs.items():
            frame = frames.get(pc, [])
            functions[frame[0][0] if frame else "unknown"] += count
            if any(name == "benchmark_body" for name, _ in frame):
                body_ops[opcodes.get(pc, "?")] += count
        if not pcs:
            raise AssertionError("Missing Spike PC histogram")
        return dict(
            scope="Whole run, including warmup, setup and verification",
            total_instructions=sum(pcs.values()),
            function_counts=dict(functions.most_common()),
            body_opcode_counts=dict(body_ops.most_common()),
        )

    for level in (2, 3):
        for mode in ("baseline", "add-only", "full"):
            label = f"O{level}-{mode}"
            obj, elf = output / (label + ".o"), output / (label + ".elf")
            flags = ["-mllvm", "-riscv-seal5-regpair-bitops=false"] if mode == "add-only" else []
            if args.profile:
                flags += ["-gline-tables-only", "-gdwarf-4"]
            run(
                label + "-compile",
                [
                    args.bin / "clang",
                    "--target=riscv32",
                    "-march=rv32im" + ("xregpairs" if mode != "baseline" else ""),
                    "-mabi=ilp32",
                    f"-O{level}",
                    *flags,
                    "-ffreestanding",
                    "-ffunction-sections",
                    "-fdata-sections",
                    "-isystem",
                    args.gcc.parent.parent / "riscv64-unknown-elf/include",
                    "-I",
                    support,
                    "-DCPU_MHZ=1",
                    "-c",
                    source,
                    "-o",
                    obj,
                ],
            )
            dis, _ = run(label + "-disassembly", [args.bin / "llvm-objdump", "-d", "--mattr=+xregpairs", obj])
            run(
                label + "-link",
                [
                    args.gcc,
                    "-march=rv32im_zicsr_zicntr",
                    "-mabi=ilp32",
                    "-O2",
                    "-DCPU_MHZ=1",
                    "-I",
                    support,
                    "-nostartfiles",
                    f'-Wl,-T,{runtime / "link.ld"}',
                    "-Wl,--gc-sections",
                    runtime / "start.S",
                    runtime / "main.c",
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
                    *(["-g"] if args.profile else []),
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
                label=label,
                instructions=measurement["instructions"],
                benchmark_verified=True,
                static_pair_instructions=len(re.findall(r"\bpair\.", dis)),
            )
            if (record["static_pair_instructions"] > 0) != (mode != "baseline"):
                raise AssertionError((label, "Unexpected instruction selection"))
            if args.profile:
                record["profile"] = profile(label, elf, stderr)
            records.append(record)
            (output / "results.json").write_text(
                json.dumps(
                    dict(
                        source_sha256=hashlib.sha256(source.read_bytes()).hexdigest(),
                        compiler_version=subprocess.check_output(
                            [args.bin / "clang", "--version"], text=True
                        ).splitlines()[0],
                        measurement="Retired instructions within benchmark(), excluding warmup and verification",
                        records=records,
                    ),
                    indent=2,
                )
                + "\n"
            )
            print({k: v for k, v in record.items() if k != "profile"}, flush=True)


if __name__ == "__main__":
    main()

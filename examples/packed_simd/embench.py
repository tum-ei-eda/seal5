#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Measure automatic packed SIMD vectorization of unmodified Embench C sources.

This is a compile-only experiment, not a benchmark execution or speedup result.
"""

import argparse
from collections import Counter
import hashlib
import json
from pathlib import Path
import re
import resource
import subprocess

VARIANTS = {
    "scalar": ("+m,-gpr32v,-xpackedsimd32", False),
    "native": ("+m,-gpr32v,-xpackedsimd32", True),
    "packed": ("+m,+gpr32v,+xpackedsimd32", True),
}
VECTOR_OP = re.compile(
    r"\b(add|sub|mul|and|or|xor|shl|lshr|ashr|icmp|select|load|store)\b[^\n]*?(<\d+ x (?:i\d+|float|double)>)"
)


def execute(command, prefix):
    prefix.parent.mkdir(parents=True, exist_ok=True)
    command = list(map(str, command))
    prefix.with_suffix(".command.json").write_text(json.dumps(command, indent=2) + "\n")
    try:
        result = subprocess.run(command, capture_output=True, text=True, timeout=180)
        code, stdout, stderr = result.returncode, result.stdout, result.stderr
    except subprocess.TimeoutExpired as error:
        code, stdout, stderr = 124, str(error.stdout or ""), str(error.stderr or "")
    prefix.with_suffix(".stdout").write_text(stdout)
    prefix.with_suffix(".stderr").write_text(stderr)
    return code, stdout, stderr


def text_bytes(disassembly):
    # Count bytes only in executable .text sections, excluding constants/debug data.
    sections = re.findall(r"^\s*\d+\s+(\.text\S*)\s+([0-9a-fA-F]+)\s", disassembly, re.MULTILINE)
    return sum(int(size, 16) for _, size in sections)


def summarize(report):
    lines = [
        "# Embench packed SIMD compilation report",
        "",
        f"Memory model: {report.get('memory_model', 'strict')}.",
        "",
        "Unmodified C; RV32IM/ILP32; O3; no LTO. No forced vector widths or profitability thresholds.",
        "Scalar disables both vectorizers; native uses normal vectorizers without GPR32V; "
        "packed enables GPR32V and the demo ISA.",
        "Counts are translation units, not runtime tests. Text sizes are unlinked object text sections.",
        "",
        "| LLVM | Variant | Frontend | Optimized | DAG objects | GISel objects | "
        "Units with packed instructions (DAG / GISel) |",
        "|---|---|---:|---:|---:|---:|---:|",
    ]
    for version in report["toolchains"]:
        for variant in report.get("variants", VARIANTS):
            rows = [r for r in report["records"] if str(r["llvm"]) == version and r["variant"] == variant]
            sums = [sum(r.get(key) == 0 for r in rows) for key in ("frontend_exit", "optimizer_exit")]
            objects = [
                sum(r.get("selectors", {}).get(s, {}).get("exit_code") == 0 for r in rows) for s in ("dag", "gisel")
            ]
            selected = [
                sum(bool(r.get("selectors", {}).get(s, {}).get("packed_instructions")) for r in rows)
                for s in ("dag", "gisel")
            ]
            lines.append(
                f"| {version} | {variant} | {sums[0]}/{len(rows)} | {sums[1]} | "
                f"{objects[0]} | {objects[1]} | {selected[0]} / {selected[1]} |"
            )
    lines += ["", "## Packed candidates and failures", ""]
    for row in report["records"]:
        if (
            row.get("frontend_exit", 0)
            or row.get("vector_operations")
            or row.get("optimizer_exit", 0)
            or any(s.get("exit_code") for s in row.get("selectors", {}).values())
        ):
            counts = {s: v.get("packed_instructions", {}) for s, v in row.get("selectors", {}).items()}
            failures = {s: v["exit_code"] for s, v in row.get("selectors", {}).items() if v["exit_code"]}
            lines.append(
                f"- LLVM {row['llvm']} {row['variant']} `{row['source']}`: "
                f"vector IR {row.get('vector_operations', {})}; packed {counts}; "
                f"frontend exit {row.get('frontend_exit')}; opt exit {row.get('optimizer_exit')}; "
                f"codegen failures {failures}."
            )
    lines += [
        "",
        "Commands, optimizer remarks, IR, disassembly and failures are retained beside results.json.",
        "This report establishes compile/selection coverage only; "
        "it does not establish correctness or runtime performance.",
    ]
    return "\n".join(lines) + "\n"


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", required=True, type=Path, help="Embench tree containing src/ and support/")
    parser.add_argument("--headers", required=True, type=Path, help="RISC-V C library include directory")
    parser.add_argument("--llvm22-bin", type=Path)
    parser.add_argument("--llvm23-bin", type=Path)
    parser.add_argument("--llvm22-clang", type=Path)
    parser.add_argument("--llvm23-clang", type=Path)
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument("--benchmarks", nargs="+", help="Optional benchmark directory names")
    parser.add_argument(
        "--memory-model",
        choices=("strict", "unaligned"),
        default="strict",
        help="Whether scalar hardware supports efficient unaligned word transfers",
    )
    parser.add_argument("--variants", nargs="+", choices=VARIANTS, default=list(VARIANTS))
    args = parser.parse_args()
    resource.setrlimit(resource.RLIMIT_CORE, (0, 0))
    source, output = args.source.resolve(), args.output.resolve()
    output.mkdir(parents=True, exist_ok=True)
    sources = sorted((source / "src").glob("*/*.c"))
    if args.benchmarks:
        sources = [p for p in sources if p.parent.name in args.benchmarks]
    if not sources:
        parser.error("No benchmark C files found")
    report = {
        "source": str(source),
        "headers": str(args.headers.resolve()),
        "source_sha256": {},
        "toolchains": {},
        "variants": args.variants,
        "memory_model": args.memory_model,
        "records": [],
    }
    for path in sorted(source.rglob("*")):
        if path.is_file() and path.suffix in (".c", ".h"):
            report["source_sha256"][str(path.relative_to(source))] = hashlib.sha256(path.read_bytes()).hexdigest()
    for version in (22, 23):
        binary = getattr(args, f"llvm{version}_bin")
        if binary is None:
            continue
        binary = binary.resolve()
        clang = (getattr(args, f"llvm{version}_clang") or binary / "clang").resolve()
        report["toolchains"][str(version)] = {}
        for tool in (clang, binary / "opt", binary / "llc"):
            result = subprocess.run([str(tool), "--version"], capture_output=True, text=True, check=True)
            report["toolchains"][str(version)][str(tool)] = result.stdout
        for file in sources:
            relative = str(file.relative_to(source))
            folder = output / str(version) / file.parent.name / file.stem
            raw = folder / "input.ll"
            frontend, _, _ = execute(
                [
                    clang,
                    "--target=riscv32-unknown-elf",
                    "-march=rv32im",
                    "-mabi=ilp32",
                    "-O3",
                    "-Xclang",
                    "-disable-llvm-passes",
                    "-ffreestanding",
                    "-gline-tables-only",
                    "-isystem",
                    args.headers.resolve(),
                    "-I",
                    source / "support",
                    "-DCPU_MHZ=1",
                    "-S",
                    "-emit-llvm",
                    file,
                    "-o",
                    raw,
                ],
                folder / "frontend",
            )
            if frontend == 0:
                # The optimizer invocation controls features for this experiment. This
                # also removes unrelated generated extensions advertised by demo Clang.
                raw.write_text(re.sub(r' "target-features"="[^"]*"', "", raw.read_text()))
            for variant in args.variants:
                row = {"llvm": version, "variant": variant, "source": relative, "frontend_exit": frontend}
                report["records"].append(row)
                if frontend:
                    continue
                attrs, vectorize = VARIANTS[variant]
                if args.memory_model == "unaligned":
                    attrs += ",+unaligned-scalar-mem"
                dest = folder / variant
                optimized = dest / "optimized.ll"
                command = [
                    binary / "opt",
                    "-S",
                    "-passes=default<O3>",
                    "-mtriple=riscv32-unknown-elf",
                    f"-mattr={attrs}",
                    "-pass-remarks=.*vector.*",
                    "-pass-remarks-missed=.*vector.*",
                    "-pass-remarks-analysis=.*vector.*",
                    raw,
                    "-o",
                    optimized,
                ]
                if not vectorize:
                    command += ["-vectorize-loops=false", "-vectorize-slp=false"]
                code, _, remarks = execute(command, dest / "optimizer")
                row["vectorization_remarks"] = [
                    line
                    for line in remarks.splitlines()
                    if re.search(r": .*?\b(?:vectorized loop|SLP vectorized)\b", line)
                ]
                row["optimizer_exit"] = code
                if code == 0:
                    row["vector_operations"] = dict(
                        Counter(f"{op} {ty}" for op, ty in VECTOR_OP.findall(optimized.read_text()))
                    )
                    row["selectors"] = {}
                    for selector in ("dag", "gisel"):
                        obj = dest / f"{selector}.o"
                        command = [
                            binary / "llc",
                            "-O3",
                            "-mtriple=riscv32-unknown-elf",
                            f"-mattr={attrs}",
                            f"-global-isel={int(selector == 'gisel')}",
                            "-global-isel-abort=1",
                            "-verify-machineinstrs",
                            "-filetype=obj",
                            optimized,
                            "-o",
                            obj,
                        ]
                        code, _, diagnostics = execute(command, dest / selector)
                        selected = {"exit_code": code}
                        if code:
                            selected["diagnostic"] = next(
                                (
                                    line[:512]
                                    for line in diagnostics.splitlines()
                                    if "LLVM ERROR:" in line or "Assertion" in line
                                ),
                                diagnostics[:512],
                            )
                        row["selectors"][selector] = selected
                        if code == 0:
                            decode, asm, _ = execute(
                                [binary / "llvm-objdump", "-d", "-h", f"--mattr={attrs}", obj],
                                dest / f"{selector}-disassembly",
                            )
                            selected.update(decode_exit=decode, text_bytes=text_bytes(asm))
                            # Objdump prefixes the mnemonic with an address and encoded bytes.
                            selected["packed_instructions"] = dict(
                                Counter(re.findall(r"\bpack\.(?:add|sub)\.(?:4x8|2x16)\b", asm))
                            )
                print(version, variant, relative, "opt", row.get("optimizer_exit"), flush=True)
                (output / "results.json").write_text(json.dumps(report, indent=2) + "\n")
    if not report["toolchains"]:
        parser.error("Specify --llvm22-bin and/or --llvm23-bin")
    (output / "results.json").write_text(json.dumps(report, indent=2) + "\n")
    (output / "report.md").write_text(summarize(report))
    print(output / "report.md")


if __name__ == "__main__":
    main()

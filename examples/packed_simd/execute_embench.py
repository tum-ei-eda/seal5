#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Link and verify Embench compilation results using the demo Spike extension.

Spike's CPI=1 model reports instruction counts, not hardware cycle performance.
"""

import argparse
from collections import defaultdict
import json
from pathlib import Path
import re
import subprocess

from embench import execute, text_bytes

RUNTIME = Path(__file__).resolve().parent / "runtime"


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--results", required=True, type=Path)
    parser.add_argument("--gcc", required=True, type=Path)
    parser.add_argument("--spike", required=True, type=Path)
    parser.add_argument("--spike-source", required=True, type=Path)
    parser.add_argument("--spike-build", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument("--benchmarks", nargs="+")
    parser.add_argument("--repetitions", type=int, default=3)
    args = parser.parse_args()
    args.output = args.output.resolve()
    args.output.mkdir(parents=True, exist_ok=True)
    if args.repetitions < 1:
        parser.error("--repetitions must be positive")
    inputs = json.loads(args.results.read_text())
    source = Path(inputs["source"])
    isa = "RV32IM_Zicsr_Zicntr" + ("_Zicclsm" if inputs.get("memory_model") == "unaligned" else "")
    report = {
        "input_results": str(args.results.resolve()),
        "records": [],
        "cycle_model": "Spike CPI=1; not hardware timing",
    }
    report["spike_version"] = subprocess.run([str(args.spike), "--help"], capture_output=True, text=True).stderr
    plugin = args.output / "libseal5-packed.so"
    code, _, _ = execute(
        [
            "c++",
            "-std=c++17",
            "-fPIC",
            "-shared",
            f"-I{args.spike_source / 'riscv'}",
            f"-I{args.spike_source}",
            f"-I{args.spike_build}",
            RUNTIME / "spike.cc",
            "-o",
            plugin,
        ],
        args.output / "plugin-build",
    )
    if code:
        raise RuntimeError("Spike extension build failed; see plugin-build.stderr")
    gcc = [
        args.gcc,
        "-march=rv32im_zicsr_zicntr",
        "-mabi=ilp32",
        "-O2",
        "-DCPU_MHZ=1",
        "-ffunction-sections",
        "-fdata-sections",
        "-I",
        source / "support",
        "-nostartfiles",
        f"-Wl,-T,{RUNTIME / 'link.ld'}",
        "-Wl,--gc-sections",
        RUNTIME / "start.S",
        RUNTIME / "main.c",
    ]

    def run_guest(objects, folder):
        elf = folder / "benchmark.elf"
        code, _, _ = execute([*gcc, *objects, "-lm", "-lc", "-lgcc", "-lnosys", "-o", elf], folder / "link")
        result = {"link_exit": code, "executions": []}
        if code:
            return result
        objdump = args.gcc.with_name(args.gcc.name.replace("gcc", "objdump"))
        code, headers, _ = execute([objdump, "-h", elf], folder / "sections")
        if code == 0:
            result["linked_text_bytes"] = text_bytes(headers)
        for i in range(args.repetitions):
            code, _, stderr = execute(
                [args.spike, f"--isa={isa}", "-m128", f"--extlib={plugin}", "--extension=seal5_packed", elf],
                folder / f"run-{i}",
            )
            measurement = re.search(r"SEAL5_MEASURE (\{[^\n]*\})", stderr)
            sample = {"exit_code": code, "verified": code == 0 and measurement is not None}
            if measurement:
                sample.update(json.loads(measurement.group(1)))
            result["executions"].append(sample)
            if code:
                break
        return result

    report["extension_self_test"] = run_guest([RUNTIME / "check.c"], args.output / "extension-check")
    if (
        not all(x["verified"] for x in report["extension_self_test"]["executions"])
        or not report["extension_self_test"]["executions"]
    ):
        (args.output / "results.json").write_text(json.dumps(report, indent=2) + "\n")
        raise RuntimeError("Packed extension boundary/random/alias/x0 self-test failed")
    report["codegen_self_tests"] = []
    for version, toolchain in inputs["toolchains"].items():
        llc = next(Path(path) for path in toolchain if Path(path).name == "llc")
        for selector in (0, 1):
            folder = args.output / "codegen-check" / version / str(selector)
            objects = []
            for name in ("packed_fallback", "pack_add_4x8"):
                obj = folder / f"{name}.o"
                ir = RUNTIME.parent / "tests" / f"{name}.test-cg.ll"
                code, _, _ = execute(
                    [
                        llc,
                        "-O2",
                        "-mtriple=riscv32",
                        "-mattr=+m,+gpr32v,+xpackedsimd32",
                        f"-global-isel={selector}",
                        "-global-isel-abort=1",
                        "-verify-machineinstrs",
                        "-filetype=obj",
                        ir,
                        "-o",
                        obj,
                    ],
                    folder / f"{name}-compile",
                )
                if code:
                    raise RuntimeError(f"Codegen self-test compilation failed: {folder}")
                objects.append(obj)
            check = run_guest([RUNTIME / "check_fallback.c", *objects], folder)
            check.update(llvm=version, selector=selector)
            report["codegen_self_tests"].append(check)
            if not check["executions"] or not all(x["verified"] for x in check["executions"]):
                (args.output / "results.json").write_text(json.dumps(report, indent=2) + "\n")
                raise RuntimeError(f"Codegen shuffle/DSP/narrowing/PHI self-test failed: {folder}")
    groups = defaultdict(list)
    for record in inputs["records"]:
        program = Path(record["source"]).parent.name
        if args.benchmarks and program not in args.benchmarks:
            continue
        groups[record["llvm"], record["variant"], program].append(record)
    for (version, variant, program), records in sorted(groups.items()):
        for selector in ("dag", "gisel"):
            row = {"llvm": version, "variant": variant, "program": program, "selector": selector}
            report["records"].append(row)
            if any(r.get("selectors", {}).get(selector, {}).get("exit_code") != 0 for r in records):
                row["skipped"] = "Compilation failed for at least one translation unit"
                continue
            objects = [
                args.results.resolve().parent
                / str(version)
                / program
                / Path(r["source"]).stem
                / variant
                / f"{selector}.o"
                for r in records
            ]
            folder = args.output / str(version) / program / variant / selector
            row.update(run_guest([source / "support/beebsc.c", *objects], folder))
            print(
                version, program, variant, selector, "verified", [x["verified"] for x in row["executions"]], flush=True
            )
            (args.output / "results.json").write_text(json.dumps(report, indent=2) + "\n")
    (args.output / "results.json").write_text(json.dumps(report, indent=2) + "\n")
    print(args.output / "results.json")


if __name__ == "__main__":
    main()

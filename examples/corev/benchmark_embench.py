#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Compile and verify baseline/SEAL5 CORE-V Embench using LLVM and ETISS.

Records model cycles separately from independently instrumented instructions.
All commands, diagnostics, IR, objects and disassembly remain in --output.
"""
import argparse
from collections import Counter
from concurrent.futures import ThreadPoolExecutor, as_completed
import hashlib
import json
from pathlib import Path
import re
import resource
import statistics
import subprocess
import time

RUNTIME = Path(__file__).resolve().parent / "benchmark_runtime"
EXTENSIONS = ("xcorevalu", "xcorevbitmanip", "xcorevbi", "xcorevmac", "xcorevmem", "xcorevsimd")


def execute(command, prefix, *, timeout=180, cwd=None):
    prefix.parent.mkdir(parents=True, exist_ok=True)
    command = list(map(str, command))
    prefix.with_suffix(".command.json").write_text(json.dumps(command, indent=2) + "\n")
    started = time.monotonic()
    stdout_path, stderr_path = prefix.with_suffix(".stdout"), prefix.with_suffix(".stderr")
    with stdout_path.open("wb") as stdout_file, stderr_path.open("wb") as stderr_file:
        try:
            proc = subprocess.run(command, cwd=cwd, stdout=stdout_file, stderr=stderr_file, timeout=timeout)
            code = proc.returncode
        except subprocess.TimeoutExpired:
            code = 124

    def read_output(path):
        # Bound Python memory even if a failed simulator emits repeated traps.
        with path.open("rb") as file:
            data = file.read(1 << 20)
            if path.stat().st_size > 1 << 20:
                file.seek(max(1 << 20, path.stat().st_size - (1 << 20)))
                data += b"\n[Middle omitted from in-memory diagnostics]\n" + file.read()
        return data.decode(errors="replace")

    stdout, stderr = read_output(stdout_path), read_output(stderr_path)
    return code, stdout, stderr, time.monotonic() - started


def features(variant):
    sign = "+" if variant == "corev" else "-"
    return ",".join(
        ["+m", "-a", "-c", "-f", "-d", "-unaligned-scalar-mem", sign + "gpr32v", *(sign + ext for ext in EXTENSIONS)]
    )


def save(report, output):
    temporary = output / "results.json.tmp"
    temporary.write_text(json.dumps(report, indent=2) + "\n")
    temporary.replace(output / "results.json")


def summarize(report):
    lines = [
        "# LLVM 22 SEAL5 CORE-V Embench",
        "",
        report["method"] + ".",
        "",
        report["measurement"],
        "",
        "The same baseline GCC startup, support library and Newlib are linked into both variants. "
        "The benchmark C translation units are compiled by the same LLVM toolchain. "
        "CPU_MHZ=1 and warm_caches(1); no source changes or forced vector widths.",
        "",
        "Instruction counts are medians over verified repetitions. Ratios include only pairs that verify. "
        "Text sizes are linked .text, including the shared runtime and libraries.",
        "",
        "| Program | Baseline | CORE-V | Baseline instructions | CORE-V instructions | "
        "Instruction ratio (baseline / CORE-V) | Text bytes (baseline / CORE-V) |",
        "|---|---|---|---:|---:|---:|---:|",
    ]
    rows = {(r["program"], r["variant"]): r for r in report["records"]}
    ratios = []
    for program in sorted({r["program"] for r in report["records"]}):
        base, corev = (rows.get((program, v), {}) for v in ("baseline", "corev"))
        counts = [
            statistics.median(s["instructions"] for s in r["executions"]) if r.get("status") == "verified" else None
            for r in (base, corev)
        ]
        ratio = counts[0] / counts[1] if all(counts) else None
        if ratio is not None:
            ratios.append(ratio)
        lines.append(
            f"| {program} | {base.get('status', 'pending')} | {corev.get('status', 'pending')} | "
            f"{counts[0] if counts[0] is not None else '—'} | {counts[1] if counts[1] is not None else '—'} | "
            f"{f'{ratio:.4f}' if ratio else '—'} | "
            f"{base.get('linked_text_bytes', '—')} / {corev.get('linked_text_bytes', '—')} |"
        )
    if ratios:
        lines += [
            "",
            f"Geometric mean instruction ratio over {len(ratios)} verified pairs: "
            f"{statistics.geometric_mean(ratios):.4f}.",
        ]
    lines += ["", "## Executed custom instructions", ""]
    for row in report["records"]:
        if row["variant"] == "corev" and row.get("status") == "verified":
            custom = {k: v for k, v in row["executions"][0]["mnemonics"].items() if k.lower().startswith("cv")}
            lines.append(
                f"- {row['program']}: " + (", ".join(f"`{k}` × {v}" for k, v in sorted(custom.items())) or "none")
            )
    lines += ["", "## Failures", ""]
    for row in report["records"]:
        if row.get("status") != "verified":
            diagnostics = [s.get("failure_reason") for s in row.get("executions", []) if s.get("failure_reason")]
            diagnostics += [u["diagnostic"].splitlines()[0] for u in row.get("units", []) if u.get("diagnostic")]
            lines.append(
                f"- {row['program']} / {row['variant']}: {row.get('status')}. "
                + ("; ".join(diagnostics) if diagnostics else "See command, stderr and stdout artifacts.")
            )
    lines += [
        "",
        "Full commands, source hashes, tool versions, disassembly and per-repetition counts "
        "are retained with results.json.",
    ]
    return "\n".join(lines) + "\n"


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", required=True, type=Path)
    parser.add_argument("--llvm-bin", required=True, type=Path)
    parser.add_argument("--gcc", required=True, type=Path)
    parser.add_argument("--etiss-prefix", required=True, type=Path)
    parser.add_argument("--etiss-examples", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument("--benchmarks", nargs="+")
    parser.add_argument("--repetitions", type=int, default=3)
    parser.add_argument("--jobs", type=int, default=2)
    parser.add_argument("--run-timeout", type=int, default=300)
    args = parser.parse_args()
    if min(args.repetitions, args.jobs, args.run_timeout) < 1:
        parser.error("repetitions, jobs and run-timeout must be positive")
    resource.setrlimit(resource.RLIMIT_CORE, (0, 0))
    for key in ("source", "llvm_bin", "gcc", "etiss_prefix", "etiss_examples", "output"):
        setattr(args, key, getattr(args, key).resolve())
    out, llvm, source = args.output, args.llvm_bin, args.source
    out.mkdir(parents=True, exist_ok=True)
    support = out / "runtime"
    support.mkdir(exist_ok=True)
    report = {
        "configuration": {key: str(value) if isinstance(value, Path) else value for key, value in vars(args).items()},
        "method": "RV32IM/ILP32, strict alignment, O3, normal vectorizer profitability, no LTO; "
        "GlobalISel with fallback disabled",
        "measurement": "Independent host-side instruction instrumentation between seal5_measure_start/end; "
        "includes marker/call overhead. ETISS cycles are a model, not hardware timing. "
        "Initialization, warmup and verification excluded.",
        "versions": {},
        "source_sha256": {},
        "records": [],
    }
    report["artifact_sha256"] = {}
    for path in [
        Path(__file__),
        *RUNTIME.glob("*"),
        args.etiss_prefix / "lib/libETISS.so",
        args.etiss_prefix / "lib/plugins/libRV32IMACFDXCoreV.so",
        *(llvm / name for name in ("clang", "opt", "llc", "llvm-objdump")),
        args.gcc,
    ]:
        if path.is_file():
            report["artifact_sha256"][str(path.resolve())] = hashlib.sha256(path.read_bytes()).hexdigest()
    for path in sorted(source.rglob("*")):
        if path.is_file() and path.suffix in (".c", ".h"):
            report["source_sha256"][str(path.relative_to(source))] = hashlib.sha256(path.read_bytes()).hexdigest()
    for tool in (llvm / "clang", llvm / "opt", llvm / "llc", args.gcc):
        code, stdout, stderr, _ = execute([tool, "--version"], support / (tool.name + "-version"))
        if code:
            raise RuntimeError(f"Tool unavailable: {tool}: {stderr}")
        report["versions"][str(tool)] = stdout
    root = Path(subprocess.check_output([args.gcc, "-print-sysroot"], text=True).strip())
    headers = root / "include"
    gccflags = [args.gcc, "-march=rv32im_zicsr", "-mabi=ilp32", "-O2", "-ffunction-sections", "-fdata-sections"]
    # Build common runtime with the same baseline GCC and libraries for both variants.
    for name in ("crt0.S", "trap_handler.c", "fixes.c"):
        code, _, stderr, _ = execute(
            [
                *gccflags,
                "-I",
                args.etiss_examples / "riscv_crt0",
                "-c",
                args.etiss_examples / "riscv_crt0" / name,
                "-o",
                support / (name + ".o"),
            ],
            support / ("compile-" + name),
        )
        if code:
            raise RuntimeError(f"Runtime build failed: {name}: {stderr}")
    for name, path in (("main", RUNTIME / "main.c"), ("beebsc", source / "support/beebsc.c")):
        code, _, stderr, _ = execute(
            [*gccflags, "-DCPU_MHZ=1", "-I", source / "support", "-c", path, "-o", support / (name + ".o")],
            support / ("compile-" + name),
        )
        if code:
            raise RuntimeError(f"Runtime build failed: {name}: {stderr}")
    linker = support / "etiss.ld"
    template = (args.etiss_examples / "etiss.ld.in").read_text()
    for key, value in {
        "MEM_ROM_ORIGIN": "0x10000000",
        "MEM_ROM_LENGTH": "0x01000000",
        "MEM_RAM_ORIGIN": "0x20000000",
        "MEM_RAM_LENGTH": "0x01000000",
        "MIN_STACK_SIZE": "0x10000",
        "MIN_HEAP_SIZE": "0x10000",
    }.items():
        template = template.replace("@" + key + "@", value)
    linker.write_text(template)
    includes = [
        args.etiss_prefix / "include",
        args.etiss_prefix / "include/jit",
        args.etiss_prefix / "include/third_party/betterenums",
        args.etiss_prefix / "include/third_party/simpleini",
    ]
    host = out / "etiss-counter"
    code, _, stderr, _ = execute(
        [
            "c++",
            "-std=c++17",
            "-O2",
            *(f"-I{p}" for p in includes),
            RUNTIME / "etiss_counter.cpp",
            f"-L{args.etiss_prefix / 'lib'}",
            f"-Wl,-rpath,{args.etiss_prefix / 'lib'}",
            "-lETISS",
            "-o",
            host,
        ],
        support / "counter-build",
    )
    if code:
        raise RuntimeError(f"Counter build failed: {stderr}")
    common = [support / (name + ".o") for name in ("crt0.S", "trap_handler.c", "fixes.c")]

    def link(objects, folder):
        elf = folder / "benchmark.elf"
        code, _, _, _ = execute(
            [
                *gccflags,
                "-nostartfiles",
                f"-Wl,-T,{linker}",
                "-Wl,--gc-sections",
                *common,
                *objects,
                "-Wl,--start-group",
                "-lm",
                "-lc",
                "-lsemihost",
                "-lgcc",
                "-Wl,--end-group",
                "-o",
                elf,
            ],
            folder / "link",
        )
        return code, elf

    def run(elf, folder, repeat):
        nm = args.gcc.with_name(args.gcc.name.replace("gcc", "nm"))
        code, symbols, _, _ = execute([nm, "--defined-only", elf], folder / "symbols")
        names = dict(
            (name, int(address, 16))
            for address, name in re.findall(r"^([0-9a-fA-F]+)\s+\S\s+(seal5_measure_\w+)$", symbols, re.M)
        )
        if code or len(names) != 2:
            return {"exit_code": 125, "verified": False, "error": "Missing ROI symbols"}
        run_dir = folder / f"run-{repeat}"
        run_dir.mkdir(parents=True, exist_ok=True)
        ini = run_dir / "guest.ini"
        ini.write_text(
            f"""[StringConfigurations]
vp.elf_file={elf}
jit.type=GCCJIT
etiss.output_path_prefix={run_dir}/
[BoolConfigurations]
arch.enable_semihosting=true
etiss.load_integrated_libraries=true
jit.gcc.cleanup=true
vp.quiet=true
[IntConfigurations]
simple_mem_system.memseg_origin_00=0x10000000
simple_mem_system.memseg_length_00=0x01000000
simple_mem_system.memseg_origin_01=0x20000000
simple_mem_system.memseg_length_01=0x01000000
arch.cpu_cycle_time_ps=31250
etiss.max_block_size=100
etiss.loglevel=0
seal5.roi_start={names['seal5_measure_start']}
seal5.roi_end={names['seal5_measure_end']}
"""
        )
        code, stdout, stderr, elapsed = execute(
            [host, f"-i{ini}"], run_dir / "execute", timeout=args.run_timeout, cwd=run_dir
        )
        match = re.search(r"SEAL5_COUNTS (\{[^\n]+\})", stdout)
        counts = json.loads(match.group(1)) if match else {}
        verified = (
            code == 0
            and "SEAL5_RESULT verified=1" in stdout
            and counts.get("starts") == counts.get("ends") == 1
            and counts.get("active") == 0
        )
        sample = {"exit_code": code, "verified": verified, "wall_seconds": elapsed, **counts}
        if not verified:
            exception = re.search(r"EXCEPTION:[^\n]+", stdout + stderr)
            sample["failure_reason"] = (
                exception.group(0)
                if exception
                else (
                    "Embench verification returned false"
                    if "SEAL5_RESULT verified=0" in stdout
                    else "Simulation timed out" if code == 124 else "No complete verified measurement"
                )
            )
        return sample

    check = out / "counter-check"
    check.mkdir(exist_ok=True)
    code, elf = link([RUNTIME / "counter_check.S"], check)
    report["counter_self_test"] = {"link_exit": code}
    if not code:
        report["counter_self_test"].update(run(elf, check, 0))
    save(report, out)
    sample = report["counter_self_test"]
    if (
        not sample.get("verified")
        or sample.get("instructions") != 31
        or sum(count for name, count in sample.get("mnemonics", {}).items() if name.lower().startswith("cv")) != 10
    ):
        raise RuntimeError("Instruction-counter self-test failed; see counter-check artifacts")

    programs = sorted(p for p in (source / "src").iterdir() if p.is_dir())
    if args.benchmarks:
        programs = [p for p in programs if p.name in args.benchmarks]
    if not programs:
        parser.error("No matching benchmarks")

    def benchmark(program, variant):
        folder = out / program.name / variant
        folder.mkdir(parents=True, exist_ok=True)
        row = {"program": program.name, "variant": variant, "units": [], "executions": []}
        attrs = features(variant)
        objects = []
        for path in sorted(program.glob("*.c")):
            unit = {"source": str(path.relative_to(source))}
            row["units"].append(unit)
            dest = folder / path.stem
            dest.mkdir(exist_ok=True)
            raw, optimized, obj = dest / "input.ll", dest / "optimized.ll", dest / "code.o"
            code, _, _, _ = execute(
                [
                    llvm / "clang",
                    "--target=riscv32-unknown-elf",
                    "-march=rv32im",
                    "-mabi=ilp32",
                    "-O3",
                    "-Xclang",
                    "-disable-llvm-passes",
                    "-ffreestanding",
                    "-isystem",
                    headers,
                    "-I",
                    source / "support",
                    "-DCPU_MHZ=1",
                    "-S",
                    "-emit-llvm",
                    path,
                    "-o",
                    raw,
                ],
                dest / "frontend",
            )
            unit["frontend_exit"] = code
            if code:
                continue
            raw.write_text(re.sub(r' "target-features"="[^"]*"', "", raw.read_text()))
            code, _, _, _ = execute(
                [
                    llvm / "opt",
                    "-S",
                    "-passes=default<O3>",
                    "-mtriple=riscv32-unknown-elf",
                    f"-mattr={attrs}",
                    "-pass-remarks=.*vector.*",
                    "-pass-remarks-missed=.*vector.*",
                    raw,
                    "-o",
                    optimized,
                ],
                dest / "optimizer",
            )
            unit["optimizer_exit"] = code
            if code:
                continue
            code, _, _, _ = execute(
                [
                    llvm / "llc",
                    "-O3",
                    "-mtriple=riscv32-unknown-elf",
                    f"-mattr={attrs}",
                    "-global-isel=1",
                    "-global-isel-abort=1",
                    "-verify-machineinstrs",
                    "-filetype=obj",
                    optimized,
                    "-o",
                    obj,
                ],
                dest / "codegen",
            )
            unit["codegen_exit"] = code
            if code:
                unit["diagnostic"] = (dest / "codegen.stderr").read_text()[:1000]
            if not code:
                objects.append(obj)
        if len(objects) != len(row["units"]) or not objects:
            row["status"] = "compile_failed"
            return row
        code, elf = link([support / "main.o", support / "beebsc.o", *objects], folder)
        row["link_exit"] = code
        if code:
            row["status"] = "link_failed"
            return row
        _, asm, _, _ = execute([llvm / "llvm-objdump", "-d", "-h", f"--mattr={attrs}", elf], folder / "disassembly")
        row["linked_text_bytes"] = sum(
            int(size, 16) for size in re.findall(r"^\s*\d+\s+\.text\S*\s+([0-9a-fA-F]+)\s", asm, re.M)
        )
        row["static_custom_instructions"] = dict(Counter(re.findall(r"\bseal5\.cv\.[\w.]+", asm)))
        for repeat in range(args.repetitions):
            sample = run(elf, folder, repeat)
            row["executions"].append(sample)
            if not sample["verified"]:
                break
        row["status"] = "verified" if all(s["verified"] for s in row["executions"]) else "execution_failed"
        row["deterministic_counts"] = len({s.get("instructions") for s in row["executions"]}) == 1
        return row

    with ThreadPoolExecutor(max_workers=args.jobs) as pool:
        pending = [
            pool.submit(benchmark, program, variant) for program in programs for variant in ("baseline", "corev")
        ]
        for future in as_completed(pending):
            row = future.result()
            report["records"].append(row)
            report["records"].sort(key=lambda row: (row["program"], row["variant"]))
            save(report, out)
            print(row["program"], row["variant"], row["status"], flush=True)
    print(out / "results.json", flush=True)
    (out / "report.md").write_text(summarize(report))


if __name__ == "__main__":
    main()

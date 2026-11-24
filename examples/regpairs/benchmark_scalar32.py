#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Compare scalar RV32 alternatives with the SHA-512 regpair prototype.

Funnel and SHA macros are explicitly substituted; add3 is inserted into optimized
IR. This probes feasibility and instruction counts, not automatic Seal5 selection.
"""
from pathlib import Path
import argparse
import hashlib
import subprocess
import re
import json


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    for name in ("bin", "gcc", "spike", "pair-plugin", "scalar-plugin", "marker-plugin", "source", "output"):
        parser.add_argument("--" + name, required=True, type=Path)
    args = parser.parse_args()
    root = Path(__file__).resolve().parent
    out = args.output.resolve()
    out.mkdir(parents=True, exist_ok=True)
    tools, gcc = args.bin, args.gcc
    runtime = root.parent / "packed_simd/runtime"
    upstream = args.source.read_text()
    start = upstream.index("static const uint64_t K[80]")
    end = upstream.index("\n#if !defined(MBEDTLS_DEPRECATED_REMOVED)", start)
    base = (root / "benchmark/sha512-shim.h").read_text() + upstream[start:end]
    records = []
    metadata = dict(
        source_sha256=hashlib.sha256(args.source.read_bytes()).hexdigest(),
        compiler_version=subprocess.check_output([tools / "clang", "--version"], text=True).splitlines()[0],
        selection="Explicit scalar C/IR insertion; automatic SelectionDAG for regpairs",
        measurement="Retired instructions; one verified SHA-512 abc compression call",
    )

    def run(label, cmd):
        command = list(map(str, cmd))
        r = subprocess.run(command, capture_output=True, text=True, timeout=120)
        (out / (label + ".stdout")).write_text(r.stdout)
        (out / (label + ".stderr")).write_text(r.stderr)
        (out / (label + ".command.json")).write_text(json.dumps(command) + "\n")
        if r.returncode:
            raise RuntimeError((label, r.stderr[-3000:]))
        return r.stdout, r.stderr

    for small in (False, True):
        for level in (2, 3):
            for mode in ("baseline", "zbb", "funnel", "funnel-add3", "sha512", "sha512-add3", "pairs"):
                label = f'{"small" if small else "default"}-O{level}-{mode}'
                s = base
                if mode in ("funnel", "funnel-add3"):
                    s = s.replace(
                        "#define ROTR(x, n) (SHR((x), (n)) | ((x) << (64 - (n))))",
                        "#define ROTR(x, n) scalar32_ror64((x), (n))",
                    )
                if mode in ("sha512", "sha512-add3"):
                    for macro, fn in [("S0", "sig0"), ("S1", "sig1"), ("S2", "sum0"), ("S3", "sum1")]:
                        s, n = re.subn(
                            r"^#define " + macro + r"\(x\).*$", f"#define {macro}(x) scalar32_{fn}(x)", s, flags=re.M
                        )
                        assert n == 1
                if mode not in ("baseline", "zbb", "pairs"):
                    at = s.index("static const uint64_t K[80]")
                    s = s[:at] + '\n#include "' + str(root / "benchmark/scalar32.h") + '"\n' + s[at:]
                source = out / (label + ".c")
                source.write_text(s)
                obj = out / (label + ".o")
                elf = out / (label + ".elf")
                arch = "rv32im" + (
                    "_zbb"
                    if mode == "zbb"
                    else "_zknh" if mode.startswith("sha512") else "xregpairs" if mode == "pairs" else ""
                )
                flags = [
                    tools / "clang",
                    "--target=riscv32",
                    "-march=" + arch,
                    "-mabi=ilp32",
                    f"-O{level}",
                    "-ffreestanding",
                    "-ffunction-sections",
                    "-fdata-sections",
                    "-isystem",
                    gcc.parent.parent / "riscv64-unknown-elf/include",
                ] + (["-DMBEDTLS_SHA512_SMALLER"] if small else [])
                if mode.endswith("add3"):
                    ir = out / (label + ".ll")
                    run(label + "-ir", flags + ["-S", "-emit-llvm", source, "-o", ir])
                    text = ir.read_text()
                    count = [0]

                    def replace(m):
                        count[0] += 1
                        return f"  {m[1]} = call i64 @seal5_scalar32_add64(i64 {m[2]}, i64 {m[3]})" + m[4]

                    text = re.sub(
                        r"^  (%[\w.$-]+) = add(?: nuw| nsw)* i64 ([^,]+), ([^,\n]+)([^\n]*)$", replace, text, flags=re.M
                    )
                    assert count[0] > 0
                    ir.write_text(text + "\n" + (root / "benchmark/scalar32-add64.ll").read_text())
                    run(label + "-compile", flags + ["-c", ir, "-o", obj])
                else:
                    run(label + "-compile", flags + ["-c", source, "-o", obj])
                dis, _ = run(
                    label + "-disassembly",
                    [
                        tools / "llvm-objdump",
                        "-d",
                        "--mattr=+zbb,+zknh" + (",+xregpairs" if mode == "pairs" else ""),
                        obj,
                    ],
                )
                run(
                    label + "-link",
                    [
                        gcc,
                        "-march=rv32im_zicsr_zicntr",
                        "-mabi=ilp32",
                        "-O2",
                        "-nostartfiles",
                        f'-Wl,-T,{runtime/"link.ld"}',
                        "-Wl,--gc-sections",
                        runtime / "start.S",
                        root / "benchmark/sha512-main.c",
                        obj,
                        "-lm",
                        "-lc",
                        "-lgcc",
                        "-lnosys",
                        "-o",
                        elf,
                    ],
                )
                isa = "RV32IM_Zicsr_Zicntr" + (
                    "_Zbb" if mode == "zbb" else "_Zknh" if mode.startswith("sha512") else ""
                )
                ext = "seal5_regpairs" if mode == "pairs" else "seal5_scalar32"
                plugin = args.pair_plugin if mode == "pairs" else args.scalar_plugin
                _, stderr = run(
                    label + "-execute",
                    [
                        args.spike,
                        "--isa=" + isa,
                        "-m128",
                        "--extlib=" + str(args.marker_plugin),
                        "--extlib=" + str(plugin),
                        "--extension=seal5_packed",
                        "--extension=" + ext,
                        elf,
                    ],
                )
                measure = json.loads(re.search(r"SEAL5_MEASURE (\{.*\})", stderr)[1])
                rec = dict(
                    label=label,
                    instructions=measure["instructions"],
                    sha512_instructions=len(re.findall(r"\bsha512", dis)),
                )
                words = [int(x, 16) for x in re.findall(r"^\s*[0-9a-f]+:\s+([0-9a-f]{8})\b", dis, re.M)]
                custom = [x for x in words if x & 127 == 11] if mode != "pairs" else []
                rec["static_scalar_custom"] = len(custom)
                rec["static_custom_using_odd_registers"] = sum(
                    any(
                        r & 1
                        for r in [(x >> 7) & 31, (x >> 15) & 31, (x >> 20) & 31]
                        + ([(x >> 27) & 31] if (x >> 12) & 7 == 1 else [])
                    )
                    for x in custom
                )
                if mode in ("funnel", "funnel-add3", "sha512-add3") and not custom:
                    raise AssertionError((label, "Missing scalar instructions"))
                if mode.startswith("sha512") and not rec["sha512_instructions"]:
                    raise AssertionError((label, "Missing SHA-512 instructions"))
                rec["digest_verified"] = True
                records.append(rec)
                (out / "results.json").write_text(json.dumps(dict(**metadata, records=records), indent=2) + "\n")
                print(rec, flush=True)


if __name__ == "__main__":
    main()

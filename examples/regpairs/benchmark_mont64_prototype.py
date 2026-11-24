#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Replay a mont64 baseline's captured commands with explicit ISA prototypes.

The reference directory is benchmark_mont64.py output. Source is copied to a
new directory and only two expressions in modul64 are substituted. No compiler
patches, source-cache edits or automatic pattern-selection claims are involved.
"""
import argparse
import json
from pathlib import Path
import subprocess
import re

ROOT = Path(__file__).resolve().parent


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--reference", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--spike-source", type=Path, required=True)
    parser.add_argument("--spike-build", type=Path, required=True)
    args = parser.parse_args()
    args.output.mkdir(parents=True, exist_ok=False)
    out = args.output.resolve()

    def run(label, command):
        command = list(map(str, command))
        (out / (label + ".command.json")).write_text(json.dumps(command) + "\n")
        p = subprocess.run(command, capture_output=True, text=True, timeout=120)
        (out / (label + ".stdout")).write_text(p.stdout)
        (out / (label + ".stderr")).write_text(p.stderr)
        if p.returncode:
            raise RuntimeError(f"{label}: {p.stderr[-3000:]}")
        return p.stderr

    plugin = out / "libseal5-mont64.so"
    run(
        "plugin",
        [
            "c++",
            "-std=c++17",
            "-shared",
            "-fPIC",
            "-I" + str(args.spike_source / "riscv"),
            "-I" + str(args.spike_source),
            "-I" + str(args.spike_build),
            ROOT / "benchmark/mont64-spike.cc",
            "-o",
            plugin,
        ],
    )
    records = []
    for level in (2, 3):
        prefix = f"O{level}-full"

        def load(stage):
            return json.loads((args.reference / (prefix + "-" + stage + ".command.json")).read_text())

        original_compile = load("compile")
        source = Path(original_compile[original_compile.index("-c") + 1]).read_text()
        for mode in ("control", "funnel", "compare", "both"):
            label = f"O{level}-{mode}"
            text = source
            if mode in ("funnel", "both"):
                needle = "(x << 1) | (y >> 63)"
                assert text.count(needle) == 1
                text = text.replace(needle, "mont_fsl1(x, y)")
            if mode in ("compare", "both"):
                needle = "(x | t) >= z"
                assert text.count(needle) == 1
                text = text.replace(needle, "mont_geu(x | t, z)")
            # Validate both operations outside the measured benchmark region.
            validation = """
  uint64_t seed = 1;
  for (unsigned j = 0; j < 1024; ++j) {
    seed = seed * 6364136223846793005ULL + 1;
    uint64_t a = seed;
    seed = seed * 6364136223846793005ULL + 1;
    uint64_t b = seed;
    if (mont_fsl1(a,b) != ((a << 1) | (b >> 63)) ||
        mont_geu(a,b) != (a >= b) || mont_geu(a,a) != 1 ||
        mont_geu(a,0) != 1 || mont_geu(0,a) != (a == 0)) abort();
  }
"""
            needle = "initialise_benchmark (void)\n{"
            assert needle in text
            text = text.replace(needle, needle + validation)
            generated = out / (label + ".c")
            generated.write_text(
                '#include <stdint.h>\n#include "' + str(ROOT / "benchmark/mont64-prototype.h") + '"\n' + text
            )
            obj, elf = out / (label + ".o"), out / (label + ".elf")
            command = original_compile.copy()
            command[command.index("-c") + 1] = str(generated)
            command[command.index("-o") + 1] = str(obj)
            run(label + "-compile", command)
            command = load("link")
            command = [str(obj) if x == original_compile[-1] else x for x in command]
            command[command.index("-o") + 1] = str(elf)
            run(label + "-link", command)
            command = [x for x in load("execute") if x != "-g"]
            command[-1:] = ["--extlib=" + str(plugin), "--extension=seal5_mont64", str(elf)]
            stderr = run(label + "-execute", command)
            measurement = json.loads(re.search(r"SEAL5_MEASURE (\{.*\})", stderr)[1])
            record = dict(
                label=label, instructions=measurement["instructions"], benchmark_verified=True, semantic_checks=1024
            )
            records.append(record)
            (out / "results.json").write_text(
                json.dumps(
                    dict(
                        scope="Explicit prototypes in modul64 only; allocator-selected even/odd pairs; explicit selection overhead included",
                        records=records,
                    ),
                    indent=2,
                )
                + "\n"
            )
            print(record, flush=True)


if __name__ == "__main__":
    main()

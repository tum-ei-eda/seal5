# Packed SIMD on embedded benchmarks: implemented steps

Measured 2026-11-05. Unmodified Embench C now compiles and executes with packed
instructions on LLVM 22 and 23, using ordinary TableGen patterns and both
selectors. The demonstrated reductions are **retired instructions under Spike's
CPI=1 functional model**, not hardware cycle speedups.

## Implemented changes

- Packed vector constants/construction and loop PHIs, unblocking `md5sum`.
- Scalar fallback for unsupported arithmetic, widening/narrowing, shifts,
  comparisons/selects, shuffles, concatenation, and narrow memory transfers.
  Packed word transfers retain alignment handling; scalarized stores are not
  re-merged into a legalization loop.
- `edn`'s DSP path can combine scalar multiply/shift/extension sequences with
  packed halfword addition. This does not add packed multiply instructions.
- Separate `gpr32v-add` / `gpr32v-sub` capabilities from the GPR32V representation.
  Generated ISA extensions imply the capabilities they implement. PatternGen
  enables them in its analysis target, before the generated ISA exists.
- Replace the placeholder shuffle cost with packing/extraction estimates;
  account for scalarized operations and split unaligned memory transfers. These
  are instruction-based estimates, not a calibrated microarchitecture model.
- Spike extension, boot/link support, execution and verification runner, and
  independent instruction and generated-code self-tests.

The ISA still contains four packed instructions: byte/halfword add/subtract.
RV64 and additional packed hardware operations remain outside this work.

## Experimental controls

Both LLVM versions compile 22 programs / 26 translation units as RV32IM/ILP32 at
O3, without LTO, vector intrinsics, forced vector widths or profitability
thresholds. Scalar disables vectorizers; native enables normal vectorizers
without GPR32V; packed enables the generated ISA and GPR32V. Machine verification
is enabled and GlobalISel fallback is prohibited.

Memory behavior is an explicit target choice applied to **all** configurations:

- **Strict:** unaligned words are split into scalar accesses. The revised costs
  do not select the four packed instructions in this Embench snapshot.
- **Unaligned-capable:** `+unaligned-scalar-mem`; Spike enables `Zicclsm` so the
  resulting accesses execute correctly. Normal O3 vectorization then selects
  packed halfword addition in `edn` and byte addition in `md5sum`.

`md5sum` vectorizes message-buffer initialization, not its MD5 rounds. `edn`
vectorizes DSP loops. Each measured interval calls `benchmark()` after
initialization and warmup, then calls Embench's `verify_benchmark()` outside the
interval. Counter deltas include common measurement overhead. Each binary runs
three times from a fresh simulator process; all recorded repetitions agree.
The Spike model increments cycles with retired instructions, so its cycle
counter is not an independent timing measurement.

## Coverage and correctness

Identical compilation coverage for both LLVM versions and memory configurations:

| Configuration | Optimized C files | DAG objects | GlobalISel objects |
|---|---:|---:|---:|
| Scalar | 26/26 | 26/26 | 25/26 |
| Native | 26/26 | 26/26 | 25/26 |
| Packed | 26/26 | 26/26 | 25/26 |

All linkable programs pass Embench verification: **22/22 for SelectionDAG and
21/22 for GlobalISel**, in every configuration. The GlobalISel omission is the
pre-existing `cubic` long-double comparison legalization failure; it occurs in
the scalar controls too. Across both memory models, 1,548 benchmark executions
pass verification (258 binaries per model, three repetitions each).

Replaying the original vectorized IR, without rerunning or changing the
optimizer, passes 102/104 codegen checks. The two failures are that same `cubic`
case, once per LLVM version. Thus conservative costing does not hide the earlier
unsupported-vector cases. `picojpeg` is included in both replay and execution.

Additional validation:

- 526/526 LLVM 22 and 549/549 LLVM 23 native GlobalISel/cost-model tests.
- 9/9 integrated demo codegen test files on each version.
- 65/65 Seal5 Python unit tests; changed Python files pass Flake8.
- Four extracted patterns per version, using the real Seal5 generation flow.
- Boundary/random operand tests for all four Spike instruction models, including
  lane isolation, register aliasing and x0.
- Independent scalar-reference execution checks of the generated DSP, narrowing,
  shuffle/insert/extract and loop-PHI code, with both selectors and versions.
- Backend support patches apply cleanly to matching upstream LLVM sources.

## Instruction counts and linked text size

Unaligned-capable target, comparing packed with native O3. Counts measure the
whole benchmark, not only the vectorized loops. Text includes the common runtime
and linked library code.

| LLVM | Program | Selector | Native instructions | Packed instructions (total) | Reduction | Native / packed text bytes |
|---|---|---|---:|---:|---:|---:|
| 22 | edn | DAG | 3,247,158 | 3,177,558 | 2.14% | 3,948 / 4,068 |
| 22 | edn | GISel | 3,220,983 | 3,170,959 | 1.55% | 4,032 / 4,184 |
| 23 | edn | DAG | 3,112,309 | 3,042,709 | 2.24% | 3,820 / 3,948 |
| 23 | edn | GISel | 3,086,044 | 3,036,022 | 1.62% | 3,892 / 4,052 |
| 22/23 | md5sum | DAG | 1,993,376 | 1,840,483 | 7.67% | 18,136 / 18,160 |
| 22/23 | md5sum | GISel | 2,019,546 | 1,866,665 | 7.57% | 18,196 / 18,272 |

Each measured `edn` run executes 6,525 packed halfword additions; each `md5sum`
run executes 12,750 packed byte additions. The instruction reductions come with
code-size growth. The complete comparisons, including programs without packed
instructions and strict-alignment controls, are in
[implemented-comparison.csv](implemented-comparison.csv).

## Reproduction and provenance

See [the README](../README.md#benchmark-execution-and-verification). Compile
snapshots preserve source hashes and toolchain versions; execution snapshots
summarize all repetitions, including whether their measurements agree. Full
commands, IR, disassembly, ELF files, stdout/stderr and individual samples remain
in the corresponding `/tmp/seal5-packed-complete-*` artifact directories. The
source snapshot is the same as the initial investigation; no source Git revision
is available, so its C/header SHA-256 manifest identifies it.

- [Strict compilation](implemented-compile-strict.json) and [execution](implemented-execution-strict.json).
- [Unaligned-capable compilation](implemented-compile-unaligned.json) and [execution](implemented-execution-unaligned.json).
- [Earlier-IR replay](implemented-replay.json).

CoreDSL2LLVM branch heads in `/work/git/CoreDSL2LLVM`:

- `llvm-22.1.8-packed-simd`: `4c9b23ffa790` (lowering commit `1245c3003bd0`).
- `llvm-23.1.3-packed-simd`: `f3e4c5705c2d` (lowering commit `efe799635`).

The branches are local and have not been pushed. Hardware-cycle speedups still
require a timing model or physical core implementing the chosen ISA and memory
behavior; Spike's CPI=1 results do not establish them.

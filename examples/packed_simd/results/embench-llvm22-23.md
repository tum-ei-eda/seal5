# Embench automatic packed SIMD: LLVM 22 and 23

The optimizer vectorizes real benchmark code, but the current packed backend does
not yet compile those vectorized programs successfully. **No successful complete
Embench object contains one of the four demo packed instructions.**

Measured on 2026-11-04 using an existing local Embench snapshot: 22 programs,
26 C translation units. Source files were unmodified; their C/header SHA-256
manifest is in [the machine-readable results](embench-llvm22-23.json). This
snapshot has no available Git revision and should not be described as the latest
Embench release.

## Method

Each matching-version Clang frontend emits unoptimized IR from scalar C using
RV32IM/ILP32, `-O3 -Xclang -disable-llvm-passes`, freestanding mode, Newlib headers,
and `CPU_MHZ=1`. The patched optimizer then runs `default<O3>` with remarks.
Function target-feature attributes from the frontend are removed so the selected
optimizer/backend feature set controls the experiment. No vector intrinsics,
vector-width pragmas, forced profitability thresholds, or LTO are used.

Three configurations are compared:

- **Scalar:** vectorizers disabled; GPR32V and demo ISA disabled.
- **Native:** default vectorizers; GPR32V and demo ISA disabled.
- **Packed:** default vectorizers; GPR32V and `xpackedsimd32` enabled.

Both SelectionDAG and GlobalISel compile the resulting IR, with machine
verification and GlobalISel fallback prohibited. Object disassembly determines
whether packed instructions were actually selected. All translation units must
compile before a program can count as a successful complete benchmark build.
These measurements stop before linking or execution: there are no correctness,
cycle-count, or speedup claims.

## Results

Results are identical on LLVM 22.1.8 and 23.1.3:

| Configuration | Frontend | Optimizer | DAG objects | GlobalISel objects | Objects with packed instructions |
|---|---:|---:|---:|---:|---:|
| Scalar | 26/26 | 26/26 | 26/26 | 25/26 | 0 |
| Native | 26/26 | 26/26 | 26/26 | 25/26 | 0 |
| Packed | 26/26 | 26/26 | 19/26 | 18/26 | 0 |

The GlobalISel failure shared by all configurations is `cubic`: legalization of
an `s128` floating-point comparison in `SolveCubic`. It is not introduced by the
packed configuration.

The seven additional packed-mode failures involve six benchmark programs:

| Program / translation unit | Vectorization evidence | First DAG / GlobalISel blockers |
|---|---|---|
| `edn` | Packed halfword adds; loop vectorization at width 2 | Vector construction / wider vector shifts |
| `md5sum` | Byte-vector induction and add in message-buffer initialization, not the MD5 rounds | Constant vector construction / packed loop PHI |
| `nettle-sha256` | Vector stores, shifts and comparisons | Vector construction / wider vector shifts |
| `picojpeg` | Many halfword adds/subtracts, plus multiply, shifts and selects | Constant vector construction / vector select |
| `qrduino/qrencode.c` | Packed byte store | Vector construction / `G_BUILD_VECTOR` |
| `qrduino/qrframe.c` | Narrow byte OR and store | Truncating narrow-vector store / narrow-vector OR |
| `statemate` | Byte-vector compares and stores | Truncating narrow-vector store / boolean-vector bitcast |

These are the first failures, not an exhaustive inventory of each program's
missing operations. The optimizer also forms wider and shorter vectors than the
two supported 32-bit packed types. In particular, advertising 32-bit registers
does not prevent the vectorizers from producing wider intermediate operations.

## Fixes found by this experiment

Before the fixes, packed-mode optimization asserted in 13/26 LLVM 22 translation
units and 14/26 LLVM 23 translation units. Packed vectors had reached RVV-only
extract/insert and scalarization-overhead cost queries, which require a V/Zve
vector length. Both paths now use generic costs when GPR32V is enabled without
RVV. This removes all observed optimizer assertions; it does not provide a tuned
packed cost model or fix the codegen gaps above.

CoreDSL2LLVM commits:

- LLVM 22: `7649b4dd84de` on `llvm-22.1.8-packed-simd`.
- LLVM 23: `e270b488c493` on `llvm-23.1.3-packed-simd`.

The RISC-V cost-model suites pass 75/75 and 79/79 tests respectively, including
the new packed extract/insert regression. The four synthetic packed-instruction
checks still pass with both selectors at O0/O2/O3.

## Reproduction and next work

Use [the Embench runner](../embench.py), as described in
[the example README](../README.md#embench-vectorization-experiment). The full
local artifact directory is `/tmp/seal5-packed-embench-final`: it retains each
command, frontend/optimized IR, vectorizer remarks, object disassembly and error
output. The committed JSON also records toolchain versions, source hashes,
vector IR counts, object text sizes, packed instruction counts and diagnostics.
A zero runner exit means collection completed; unsupported configurations remain
failures in the report.

The next useful gates are packed constants/build-vector handling and loop PHIs
(`md5sum` is a small real-source reproducer), followed by insert/extract, narrow
memory transfers, comparisons/selects, and the multiply/shift/extension sequences
needed by DSP and image kernels. Cost queries should then reflect which
operations the generated ISA actually implements. Runtime evaluation needs an
execution target implementing the demo ISA, linked benchmark binaries, and the
Embench verification functions before any speedup comparison.

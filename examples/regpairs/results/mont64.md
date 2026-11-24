# Embench aha-mont64: expanded pairs, profile and lowering improvement

Measured the unchanged local Embench `src/aha-mont64/mont64.c` with LLVM 23,
CPU_MHZ=1, LOCAL_SCALE_FACTOR=423 and the existing independent GCC harness.
Every variant passes Embench's `verify_benchmark`. Measurement excludes warmup
and verification. These are retired instructions under Spike, not hardware
cycles, area, power or latency measurements.

| Optimization | RV32IM | Add-only pairs | Expanded pairs | With word-cost fix |
|---|---:|---:|---:|---:|
| O2 | 5,566,792 | 5,193,708 | 4,235,229 | **4,117,602** |
| O3 | 5,551,141 | 5,178,057 | 4,219,578 | **4,101,951** |

The O3 reduction improves from 6.7% with add-only support to 24.0% with the
existing expanded extension, then to **26.1%** after the lowering fix. The fix
saves another 117,627 instructions (2.8% of the expanded-pair result), without
adding instructions to the ISA. Baseline and add-only results remain unchanged.

## Profile findings

Whole-run PC histograms include one warmup repetition plus the 423 measured
repetitions, setup and verification. They are used for hotspot attribution,
not as the measured-region totals above. DWARF inline frames identify the
innermost source function for each retired PC.

| Source function | Share before fix | Share after fix |
|---|---:|---:|
| `modul64` | 84.7% | 87.1% |
| `xbinGCD` | 6.2% | 5.8% |
| `mulul64` | 3.8% | 1.7% |
| `montmul` excluding inlined helpers | 1.0% | 1.0% |

The full Embench workload repeatedly computes a reference result and modular
conversions. It spends much more work in the shift/subtract modulus loop than
in the Montgomery multiplication kernel itself. Adding widening multiply or
multiply-accumulate first would therefore address a relatively small fraction
of this benchmark.

The hot `modul64` loop contains a two-input 64-bit funnel-left operation:

```c
x = (x << 1) | (y >> 63);
```

LLVM recognizes this as `llvm.fshl.i64(x, y, 1)`, but the current pair extension
only supports rotations with identical inputs, so the funnel operation expands
into scalar shifts and ORs. The loop also needs unsigned 64-bit comparisons,
conditional subtraction, and OR operations that currently use scalar expansion.

The next ISA candidates should therefore be a two-input pair funnel shift,
pair OR, and unsigned pair comparison support. A native OR opcode count alone
must not be treated as the number of matchable pair ORs: many ORs arise inside
other scalar expansions. No new ISA operation was added in this follow-up.

## Word-cost lowering fix

Automatically selecting pair AND for a mask with a zero 32-bit word obscured
known zeros behind an opaque pair node. Similarly, selecting a pair shift for
counts >=32 obscured the word extraction or zero/sign-filled word. This caused
some masked 32x32 products to expand as general 64x64 multiplication and added
unnecessary instructions to bit tests and word construction.

The versioned `llvm22-pair-word-costs.patch` and `llvm23-pair-word-costs.patch`
leave those cases to scalar legalization. True two-word AND and cross-word
shifts/rotates retain pair selection. Explicit builtins and assembly still
support every count from 0 to 63. A regression verifies that masked low/high
word products need exactly one MUL and one MULHU, and that a genuine two-word
mask can still select pair AND.

Validation:

- Ten pair lit tests pass on each of LLVM 22 and LLVM 23.
- Independent Spike pair execution passes at O0/O2/O3 on both versions.
- Existing CORE-V suite: 651 passed, 2 unsupported on each compiler.
- Python suite: 216 passed, 1 optional test skipped, 310 subtests passed.
- LLVM 23 SHA-512 digest checks still pass. Normal compression improves from
  7,989 to 7,909 instructions; smaller compression improves from 10,427 to
  10,269. O2/O3 agree. Historical benchmark records are retained separately.

The compilers were incrementally rebuilt in the existing isolated LLVM 22/23
validation trees. This was not a clean standalone compiler rebuild. The full
aha-mont64 performance/profile comparison used LLVM 23; LLVM 22 received lit
and runtime validation of the lowering fix.

## Reproduction

```sh
python examples/regpairs/benchmark_mont64.py \
  --embench-root /path/to/embench-iot --bin /path/to/llvm/bin \
  --gcc /path/to/riscv64-unknown-elf-gcc --spike /path/to/spike \
  --pair-plugin /path/to/libseal5-regpairs.so \
  --marker-plugin /path/to/libseal5-packed.so \
  --output /tmp/mont64-pairs --profile
```

Profiling uses the matching GCC toolchain's `addr2line` and DWARF 4 line tables.
[Mont64 records](mont64-llvm23.json) preserve before/after measurements, profiles,
the benchmark source checksum and lowering source fingerprints.
[SHA-512 follow-up records](sha512-word-costs-llvm23.json) preserve its new counts.
Original logs and binaries remain under `/tmp/seal5-mont64-regpairs-final`;
after-fix artifacts are under `/tmp/seal5-mont64-regpairs-word-costs`.

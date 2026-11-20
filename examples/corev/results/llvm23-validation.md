# LLVM 23 CORE-V validation

The LLVM 23 configuration now matches the validated LLVM 22 integration.
Shared settings live in `cfg/corev.yml`; version overlays select the matching
packed-SIMD dependency and backend patches. LLVM 22 retains its original
settings and patch definitions. Both versions load all 653 source tests.

LLVM 23.1.3 was built with assertions in `/tmp/seal5-xcorev-llvm23` using
packed-SIMD dependency `f3e4c5705c2da4ecadc2babeae356e2960220293` and merged
CDSL `56b66cfea193b28cd88ea89a684469ef76fa31cc`. The full patch sequences also
apply through SEAL5's stock-LLVM backend import and insertion-marker path for
both releases. [Machine-readable validation](llvm23-validation.json) records
patch checks, extraction details and implementation hashes.

| Check | LLVM 22 reference | LLVM 23 |
|---|---:|---:|
| Source assembly/intrinsics/builtins/codegen | 651 pass, 2 unsupported | 651 pass, 2 unsupported |
| Generated opcode-selection tests | 124 pass, 14 fail | 124 pass, same 14 fail |
| Extracted instruction descriptions | 183 successful | 183 successful |
| Skipped / failed extraction descriptions | 26 / 101 | Same 26 / 101 |

All 115 Python tests pass. Fresh LLVM 23 extraction passes 3,216 MAC cases,
3,456 rounded-ALU cases, 723 clip cases, four clip bounds proofs, two clip
specialization checks, 40,800 dot-product checks, 87,760 packed-comparison
checks, 5,940 scalar-comparison checks and three rotate guard cases. The fixed
vector splat verifier regression also passes. Regenerating tests after the
Python parser fix leaves all 183 compiled pattern artifacts unchanged.

The remaining failures are shared with LLVM 22, including disabled CLB,
signed immediate EXTRACT's s33 legalization, unsupported SIMD extraction and
the 14 exact-opcode test expectations. Their instruction lists match exactly;
this migration adds no new extraction or generated selection failures.

## Fixes

- Preserve CoreDSL widening arithmetic and memory/branch handling in shared
  configuration; LLVM 23 no longer falls back to `--no-extend`.
- Port rotate, min/max and packed-comparison support to LLVM 23, retaining RV32
  and capability guards, fallback behavior and comparison semantics.
- Increase LLVM 23's subtarget feature bitset from 384 to 448 bits. The full
  target needs 391 features plus the reserved feature slot. Every tool was built
  with the new layout. The patch guard checks the actual target source header,
  independently of the PatternGen dependency, and preserves larger bitsets.
- Recognize synthetic readonly register inputs regardless of LLVM parameter
  attribute order. LLVM 23 inserts `nofree` before `readonly`; the old parser
  missed those inputs and caused 40 additional generated-test failures. The fix
  restores the scalar register ABI without changing real memory operands.
- Accept LLVM 23's more specific extra-operand diagnostic in 24 negative assembly
  tests while retaining LLVM 22 coverage. Invalid instructions remain rejected.
- Derive the benchmark report's LLVM version from the recorded compiler version.

## Execution and performance

The [LLVM 23 Embench run](embench-llvm23-main.md) verifies all 21 supported
programs in both variants: **42 successful executions**, one per variant.
The independent counter self-test passes with exactly 31 instructions,
including ten custom additions. Both variants of `cubic` retain the existing
s128 floating-point comparison legalization failure.

CORE-V executes **4.77% fewer instructions** than the matching LLVM 23 baseline
by geometric mean, compared with **5.52% on LLVM 22**. Across compiler versions,
LLVM 23 uses 0.93% fewer baseline instructions and 0.15% fewer CORE-V instructions
by geometric mean. Some programs regress: CORE-V PicoJPEG grows 3.14%, SGLIB
1.05%, AES 0.93% and EDN 0.55%. PicoJPEG and SGLIB grow in the baseline too.
These are observed instruction-count regressions without correctness failures;
the configuration fixes do not eliminate all compiler-version performance
variation.

The [cross-version table](llvm22-23-instructions.md) includes every program and
proposes targeted IR/assembly and cost-model investigations. These performance
changes were reported before adding any speculative optimizer fixes.

This is a one-repeat compatibility run, compared against LLVM 22's three-repeat
reference. It measures executed instructions, not hardware speedup or an
official Embench score. ETISS uses the same validated model and runtime adapter
as the LLVM 22 reference; ISA semantics did not change. Raw commands, IR,
disassembly and execution output remain in `/tmp/seal5-corev-embench-llvm23`.

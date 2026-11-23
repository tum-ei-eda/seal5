# RV32 register-pair validation (LLVM 22 and LLVM 23)

## Pair logic, rotate and shifts (2026-11-23)

Added XOR64, AND64, SLLI64, SRLI64, SRAI64 and RORI64 to both source styles.
Shifts/rotate use a six-bit immediate. Both versions were generated through
SEAL5 and installed into the existing integrated assertion-enabled validation
compilers; these are incremental builds, not standalone clean builds.

| Check | Result |
|---|---|
| Python suite | 210 passed, 1 optional integration test skipped; 294 subtests |
| Pair LLVM lit tests | 9 passed on each of LLVM 22 and 23 |
| Existing CORE-V suite | 651 passed, 2 unsupported on each compiler |
| Extracted behavior vs independent reference | 3,327 cases passed |
| Extraction, including malformed rotate rejection | 17 checks passed on each compiler |
| Explicit and inferred sources | Identical reduced descriptions for all 11 instructions |
| Independent Spike execution at O0/O2/O3 | All passed on each compiler |

Execution includes builtin and ordinary C implementations, shift counts
0/1/31/32/33/63, boundary and random inputs, and the existing ABI, spill and
zero-register checks. Variable shifts/rotates compile through scalar fallback.
Assembly tests cover exact encodings, round-trip decoding, odd registers and
out-of-range immediates. Extraction rejects incorrect masks, complements and
shift values instead of treating them as rotates.

### Mbed TLS SHA-512

Measured the unchanged Mbed TLS 2.28.10 compression function with the runner in
`../benchmark_sha512.py`. The baseline GCC harness checks the digest of `abc`
after every run. Counts include the compression call and common zeroization;
setup and verification are outside the measured region. No source intrinsics
were added to the SHA-512 function. The add-only variant disables automatic
new bit-operation selection with `-mllvm -riscv-seal5-regpair-bitops=false`,
keeping ADD64 enabled. Disassembly assertions verify the intended selection.

O2 and O3 gave identical counts for every row:

| LLVM | Implementation | RV32IM | Add-only pairs | Full pairs | Reduction vs RV32IM |
|---|---|---:|---:|---:|---:|
| 23 | Normal | 14,293 | 12,568 | 7,989 | 44.1% |
| 23 | `MBEDTLS_SHA512_SMALLER` | 17,217 | 15,018 | 10,427 | 39.4% |
| 22 | Normal | 15,451 | 12,766 | 7,813 | 49.4% |
| 22 | `MBEDTLS_SHA512_SMALLER` | 17,938 | 16,458 | 10,829 | 39.6% |

On LLVM 23 the new operations reduce instructions by a further 36.4% (normal)
or 30.6% (smaller) relative to add-only pairs. These are retired-instruction
measurements under Spike, not hardware cycle speedups. Instruction latency,
implementation cost and memory behavior still need hardware evaluation.

[LLVM 23 records](sha512-llvm23.json) and [LLVM 22 records](sha512-llvm22.json)
contain the upstream source checksum and static pair instruction counts.
Full logs, objects and executables are in `/tmp/seal5-pair-sha512-23` and
`/tmp/seal5-pair-sha512-22` in this workspace.

## LLVM 22 port (2026-11-23)

Validated with assertions enabled against the integrated LLVM 22.1.8 release
source, using a separate SEAL5 model/generation directory and an incremental
build of the existing validation compiler. This was not a clean standalone
compiler rebuild. The versioned adapter uses the `llvm-22.1.8` CoreDSL2LLVM
branch; LLVM 23 retains `llvm-23.1.3-packed-simd`.

Both explicit XP and inferred word-based sources transformed successfully.
Their five generated instruction definitions, reduced inputs, and extracted
patterns are identical. The patterns also match the LLVM 23 outputs. The
compiler used those generated patterns for the following checks:

| Check | Result |
|---|---|
| Python unit suite | 209 passed, 1 optional integration test skipped |
| Register-pair LLVM lit tests on LLVM 22 | 6 passed |
| Same lit tests on LLVM 23 | 6 passed |
| Existing CORE-V tests on the updated LLVM 22 compiler | 651 passed, 2 unsupported |
| Extracted behavior vs independent arithmetic reference | 1,525 cases passed |
| Extraction structure and rejected mismatched/reversed lanes | 8 checks passed |
| Executed generated code at O0/O2/O3 under Spike | All three passed |
| Final versioned LLVM 22 patches against integrated release source | All five apply |

The LLVM tests additionally cover scalar/vector bitcasts and vector argument,
return, and call lowering, including a leading scalar argument that puts the
incoming vector at an odd ABI register position. LLVM 22 explicitly splits and
joins the two scalar ABI registers; scalar `i64` remains illegal on RV32.
Runtime checks cover boundaries, random arithmetic, odd scalar ABI alignment,
spills across a call, overlapping pairs, the zero pair, and preservation of x1.

The port also corrects the LLVM 23 extraction patch to install the early
PatternGen hook instead of duplicating pass declarations. The corrected patch
applies to its dependency source, and the LLVM 23 lit suite still passes.

## Original LLVM 23 validation


Validated on 2026-11-20 with assertions enabled, using the LLVM 23
CoreDSL2LLVM base `f3e4c5705c2da4ecadc2babeae356e2960220293`.
The example was transformed/generated with separate SEAL5 metadata and its
artifacts were installed into the existing LLVM 23 validation compiler.
This was an incremental compiler build, not a clean standalone rebuild.
All five custom instruction definitions and intrinsic/builtin declarations came
from the SEAL5 generators. No dependency repository was modified.

| Check | Result |
|---|---|
| Python unit suite | 134 passed |
| Example LLVM lit tests | 6 passed (assembler, invalid operands, intrinsics, builtins, generated selection, arithmetic/fallback) |
| Existing CORE-V source tests on the updated compiler | 651 passed, 2 unsupported |
| Extracted behavior vs independent arithmetic reference | 1,525 cases passed |
| Extraction structure, including rejected mismatched/reversed lanes | 8 checks passed |
| Executed generated code at O0/O2/O3 | All three passed under Spike |
| Patches against the configured dependency source | All five apply cleanly |
| Python lint and non-patch whitespace checks | Passed |

Execution used a baseline GCC 15.1 RV32 reference and an independent Spike
extension, with only RV32IM enabled. It checked 49 boundary input pairs,
4,096 random input pairs and 128 register-pressure cases per optimization
level. Direct LLVM intrinsic wrappers, Clang builtin wrappers, ordinary scalar
addition/subtraction and explicit two-lane vector ADD/SUB/MUL were executed.
Each corresponding object contains all five expected instruction mnemonics.
Additional checks covered an odd ABI argument position, a constant
zero operand, overlapping source/destination pairs, the `x0` zero pair, and
preservation of `x1`. The pressure function contains stack stores/reloads
across an external call. The simulator rejects odd register fields.

The `XP` emission pass was tested separately for correct concatenation and
word order, unmarked operands, unsupported offsets, explicit word slices,
coalescing complete local result writes, and preserving separate writes
when aliasing, different source values or intervening statements matter.
The original architectural bank remains `X` with 32-bit elements.
Scalar ADD64/SUB64 use two aligned `i64` loads, one arithmetic operation and
one `i64` store. The packed operations are recovered as `<2 x i32>` ADD/SUB/MUL
with one complete vector output store. All 1,525 semantic cases pass with this
normalized interface.

## Generated selection and remaining limits

| Probe | Result |
|---|---|
| ADD64/SUB64 PatternGen, custom feature | One generated pair-node pattern each |
| Packed ADD/SUB/MUL PatternGen, custom feature | One generated `v2i32` pattern each |
| Ordinary C `uint64_t` addition/subtraction | Selects `pair.add64` / `pair.sub64` |
| Explicit vector ADD/SUB/MUL, custom feature only | Selects the corresponding custom instruction |
| Scalar `i64` multiplication | Scalar fallback; does not use lane-local packed MUL |
| Aligned/unaligned vector memory and dynamic extraction | Machine verification passes |
| Disabled capability or internal features without ISA | Scalar fallback; no custom/P instructions |
| Ordinary and width-requested loops | Remain scalar |
| GlobalISel pair intrinsic, fallback prohibited | Unsupported |

The validation compiler uses the extracted patterns, with the temporary
handwritten bootstrap patterns removed. Pattern generation runs through the
normal SEAL5 flow. Generic PatternGen test generation is disabled because its
XLEN/GlobalISel assumptions do not support pairs; dedicated source tests and
execution validate the resulting SelectionDAG code. Pair extraction occurs
before legalization. Scalar ADD64/SUB64 retain carry/borrow through dedicated
untyped target nodes. Separate ADD/SUB/MUL capabilities imply the shared pair
representation, without enabling P or RVV. Disabling an implied capability
clears the parent ISA in LLVM; lowering then expands all pair arithmetic safely.
The cost fixes cover pair lane operations and avoid RVV container queries;
a complete cost model for automatic loop vectorization remains future work.

The source tests cover feature-off fallback, aligned and byte-aligned memory,
dynamic extraction and unsupported operations. Runtime checks use only RV32IM
plus the independent custom-instruction model. The compiler build remains
incremental; a clean standalone rebuild was not performed.

[Machine-readable commands, results and implementation hashes](validation.json)
include the scratch log locations. Runtime code and semantic checks are
reproducible using the commands in the [example README](../README.md).

# RV32 register-pair validation (LLVM 23)

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

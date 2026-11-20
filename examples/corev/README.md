# Full CORE-V example (LLVM 22 and LLVM 23)

## Embench execution

The [CDSL review and regeneration notes](review/README.md) describe the tested
merged upstream integration, simulator corrections and tested model inputs.
Saved measurements are in
[results](results/). The [LLVM 23 validation](results/llvm23-validation.md) records
compatibility checks and the remaining instruction-count regressions.

`benchmark_embench.py` compares RV32IM with the generated full CORE-V target
using the selected LLVM frontend, `-O3` pipeline, and GlobalISel backend.
GlobalISel fallback is disabled. Both variants use normal vectorization
profitability, strict alignment, ILP32, and identical baseline GCC startup,
support routines and Newlib. The Embench C sources are unchanged.

```sh
python examples/corev/benchmark_embench.py \
  --source /path/to/embench-iot \
  --llvm-bin /path/to/corev-llvm22/build/bin \
  --gcc /path/to/riscv64-unknown-elf-gcc \
  --etiss-prefix /path/to/etiss/install \
  --etiss-examples /path/to/etiss_riscv_examples \
  --output /tmp/seal5-corev-embench --repetitions 3 --jobs 2
```

ETISS must include the matching `RV32IMACFDXCoreV` model and GCCJIT. The GCC
installation must provide RV32IM Newlib and `libsemihost`. The examples tree
supplies `riscv_crt0` and `etiss.ld.in`. Add `--benchmarks crc32 edn` for a
pilot. Compilation failures, linking failures, timeouts and failed Embench
verification remain explicit in `results.json`; only verified pairs enter
the instruction-count comparison.

The host counter instruments each executed instruction between two marker
symbols around `benchmark()`. Initialization, one warmup and verification
are outside that region; marker/call overhead is included. A self-test
requires exactly 31 instructions, including ten custom instructions.
The runner does not use ETISS's cycle-derived `instret` CSR. Model cycles
are recorded separately and do not establish hardware speedups. The
linked text size includes the common runtime and libraries. Commands,
diagnostics, IR, disassembly and per-repetition counts remain in the output
directory, alongside `results.json` and `report.md`.

## Building the example

Run from the repository root with the Python environment activated:

```sh
LLVM_REF=llvmorg-22.1.8 SEAL5_NUM_THREADS=1 CCACHE=1 \
BUILD_CONFIG=release_assertions IGNORE_ERROR=1 TEST=1 INSTALL=0 DEPLOY=0 EXPORT=0 \
DEST=/tmp/seal5_llvm_corev_llvm22 python examples/corev_demo.py
```

Use `LLVM_REF=llvmorg-23.1.3` and a separate destination such as
`DEST=/tmp/seal5_llvm_corev_llvm23` for LLVM 23. Keep the LLVM 22 build and
benchmark artifacts separate when comparing versions.

The example includes 310 instruction descriptions from XCoreVAlu, XCoreVBitmanip,
XCoreVMac, XCoreVSimd, XCoreVMem and XCoreVBranchImmediate. Hardware loops
are not included. Upstream currently disables `CV_CLB`; its intrinsic mapping
and assembly/intrinsic checks are disabled here as well. The `alu_slet` and
`alu_sletu` intrinsic names remain compatible while their instruction mappings
use the upstream `CV_SLE` and `CV_SLEU` names and mnemonics.

The bit manipulation input wrapper supplies the missing standalone `RVI`
import without modifying the pinned upstream descriptions. Both LLVM versions load `cfg/corev.yml` for shared arithmetic typing,
capability features, memory normalization and immediate-branch patterns.
`cfg/llvm22.yml` and `cfg/llvm23.yml` select their packed-SIMD PatternGen branch
and version-specific rotate, min/max and comparison patches. LLVM 23 also
raises subtarget feature capacity to fit the full generated target. Portable patches
retain their existing filenames. Both use ordinary TableGen patterns, without
direct GISel tables. The same source tests, including SIMD C tests, run for both
versions.

Generated rules receive `AddedComplexity = 1000`, as in the normalization
and packed-SIMD examples, to expose their selection during validation. This
is a selection-priority override, not a measured instruction cost or a
claim of improved execution time.

The example preserves CoreDSL widening arithmetic during IR and pattern
extraction (`no_extend: false`). The legacy `--no-extend` mode would turn
a halfword multiply into a halfword result before extension, losing the
upper product bits. Both generation passes use the same typing mode.

The `xcorevsimd` feature enables packed 32-bit registers and the baseline
byte/halfword add/sub legalization rules. This does not make every SIMD
operation legal for autovectorization: other operations may scalarize.
Pattern extraction can also fail for individual instruction behaviors;
retaining an instruction for assembly and intrinsics does not imply that
its behavior produced a selectable pattern.

Ordinary register-offset loads/stores have codegen tests for all eight
operations. Post-increment memory instructions remain available to the
assembler, with the syntax `value, (base), increment`. Their address
writeback requires multiple outputs, which the TableGen pattern path does
not support. SIMD and memory assembly tests check concrete encodings,
including instructions without extracted patterns. Packed add/sub codegen
tests use scalar-register interfaces with vector bitcasts (the baseline
does not define a vector calling convention). They cover both byte and
halfword lanes, with both SelectionDAG and
GlobalISel; GlobalISel fallback is disabled in those tests.

The CoreDSL sources import `RVI.core_desc` through the common base lookup
path. The memory descriptions use byte ranges for halfword/word accesses;
casting a single `MEM[address]` byte would describe a different operation.
LLVM 23 validation is a separate follow-up.

The checked-in compatibility patch supplies packed operation capabilities
and scalar fallbacks when the downloaded PatternGen branch predates them.
It is skipped when the dependency already defines `FeatureGPR32VAdd`.
The register-offset assembly parser patch is also required on LLVM 22.

## LLVM 22 validation

The complete target builds with assertions enabled. The validation run uses
ordinary TableGen patterns and the packed capability compatibility patch;
no direct GISel table entries are enabled.

| Test category | Passed | Failed |
| --- | ---: | ---: |
| Checked-in assembler tests | 338 | 0 |
| Checked-in intrinsic tests | 199 | 0 |
| Checked-in builtin tests | 2 | 0 |
| Checked-in codegen tests | 108 | 0 |
| Generated pattern codegen tests | 96 | 43 |

The checked-in total is **647/647 passing**. Assembler tests cover all 311
instructions and compare each sample encoding with LLVM's native CORE-V
assembler. The new codegen tests for both immediate branches, all eight
ordinary register-offset loads/stores, four packed add/sub operations,
and 40 packed comparison forms pass. Those tests exercise both SelectionDAG and GlobalISel, with GlobalISel
fallback disabled.

All checked-in tests pass. Generated-test failures include equivalent-instruction choices
(such as byte versus halfword bitwise operations) and genuine missing
matches, including dot products. All 20 formerly failing scalar-broadcast
comparison files now pass. The 20 newly generated register-comparison files
include eight exact-opcode failures: LLVM selects the equivalent swapped
GT/GE encoding for LT/LE. The checked-in tests validate both the opcode and
operand order for those equivalent encodings. The remaining 35 generated
failures are the previously known dot-product, average, bitwise, extension,
and extraction cases. A failed
exact-instruction check therefore does not by itself prove incorrect code.
All failing checks remain enabled, without XFAIL annotations.

`IGNORE_ERROR=1` lets the experimental run finish and collect reports despite
these failures. Omit it to make the TEST stage stop on a failing check. This
is not yet a fully passing pattern-selection suite.

| Instruction set | Instructions | Extracted patterns | Failed extraction | Skipped |
| --- | ---: | ---: | ---: | ---: |
| ALU | 31 | 379 | 0 | 0 |
| Bit manipulation | 16 | 10 | 3 | 3 |
| Immediate branches | 2 | 2 | 0 | 0 |
| MAC | 18 | 390 | 0 | 0 |
| Memory | 24 | 8 | 0 | 16 |
| SIMD | 220 | 176 | 104 | 0 |
| Total | 311 | 965 | 107 | 19 |

Extraction success does not establish importer acceptance or instruction
selection. The generated TableGen pattern files total 262,272 bytes in this
run. Reports retain separate extraction, import, and match fields; unavailable
validation counts remain unknown.

MAC behavior follows the 32-bit truncation before normalization in the
[CV32E40P multiplier RTL](https://github.com/openhwgroup/cv32e40p/blob/master/rtl/cv32e40p_mult.sv).
The rounding term is zero for normalization amount zero. The extracted MAC
IR passes 3,216 constant-folding checks, covering all 32 normalization amounts
for the specialized forms and shifts 0, 1, 5 and 31 for the other forms. Reproduce them after generation with:

```sh
DEST=/tmp/seal5_llvm_corev_llvm22
python examples/corev/check_mac_semantics.py \
  "$DEST/.seal5/temp/XCoreVMac/XCoreVMac" --opt "$DEST/.seal5/build/release_assertions/bin/opt"
```

Adjust the metadata directory if a named metadata directory is used. The
factored scalar-immediate byte dot product was also checked against the
unfactored arithmetic for all 64 immediate values and four packed inputs
(256 cases). Factoring avoids TableGen's excessive enumeration of
commutable subexpressions.

## Rotate-right selection

`cv-ror.test-cg.ll` checks SelectionDAG and GlobalISel at both `-O0` and
`-O3`, with GlobalISel fallback disabled. All four configurations now emit
`seal5.cv.ror` for the register-count rotate. Masked counts and constants
0, 1, 32 and 33 are covered too. Negative checks cover disabling the rotate
capability, RV64, and a funnel shift with distinct input operands.

Two separate issues previously prevented selection. Seal5's inliner wrapped
`Return` in a type conversion before checking for a return statement, so
`rotr32` remained a call and PatternGen skipped the instruction. The fixed
inliner substitutes independent, typed argument expressions and preserves
the declared return width. Both complementary shift counts are now masked
to five bits, including the zero and overshift cases. The extracted rotate
IR passes 544 constant-folding checks against modulo-32 rotation.

The generated ISA feature now implies `FeatureSeal5Rotate32`. Its LLVM 22
compatibility patch keeps RV32 rotate-right nodes legal in both selectors.
At `-O0`, GlobalISel also needs a custom legalization step to recognize a
same-input funnel shift, because the optional combiner is disabled. A
funnel shift with distinct inputs still expands to shifts and OR. The
capability leaves the baseline policy for RV64 and rotate-left unchanged.
The ordinary TableGen rotate pattern is extracted from the description;
no handwritten instruction-selection rule or direct GISel table is used.

## Immediate specialization for multiplication

The four unrounded halfword multiply descriptions use `[[auto_unroll_imm]]`.
Seal5 marks their 5-bit `Is3` operand for specialization, and PatternGen
extracts 32 constant-folded patterns per instruction. This includes the
normalization-zero case, where the shift disappears. The four descriptions
therefore contribute 128 patterns instead of four; the ISA still contains
311 instructions. Rounded multiply/MAC and clip specialization are described
below.

The tests exercise all 128 instruction/count combinations with SelectionDAG
and GlobalISel at `-O0` and `-O3`, with fallback disabled. The original four
zero-normalization failures now pass. Register-controlled amounts cannot
be enumerated through this attribute.

Optimized GlobalISel also required a cost-model correction: constant
hoisting had hidden the `65535` masks behind `G_CONSTANT_FOLD_BARRIER` nodes.
The LLVM 22 stage-3 compatibility patch treats those masks as free only for
RV32 XCoreVMac when all their uses are multiplications with both operands
masked to 16 bits. The generated multiply consumes these masks directly.
Negative tests retain the baseline behavior for masked addition and for a
target without XCoreVMac. This does not disable constant hoisting globally.

Generated tests for specialized register-only instructions expose readonly
register inputs as scalar arguments. Local register slots are eliminated with
SROA and InstCombine before codegen, preserving the subregister extractions
that pointer-backed halfword loads previously absorbed. All four multiply
wrapper files now pass, each checking all 32 specializations. Real memory
instructions retain their pointer inputs. Generated-test labels identify each
specialized function, and opcode checks cannot match function names.
Diagnostic output is captured separately so statistics cannot interrupt a
pattern record.

The pattern report counts all 32 extracted rules for each specialized multiply,
while counting each instruction once. The MAC set now contains 18 instructions
and 390 TableGen patterns; the global totals are 311 instructions and 965 patterns.
Importer acceptance and codegen-match counts remain unknown without explicit
per-pattern validation evidence; a passing wrapper file is not treated as
proof that every extracted rule was imported or selected.

## Clip pattern selection

`CV_CLIP` and `CV_CLIPU` specialize their five-bit immediate with
`[[auto_unroll_imm]]`. The register forms mask the bound to 31 bits, as
specified by the [CORE-V general ALU operations](https://docs.openhwfoundation.org/projects/cv32e40p-user-manual/en/latest/instruction_set_extensions.html#general-alu-operations).
The previous unmasked expression describes a different operation when the
bound's sign bit is set and must not select a clip instruction.

The LLVM 22 min/max capability patch preserves scalar min/max nodes in both
selectors when XCoreVAlu is enabled. PatternGen additionally emits equivalent
clamp orders when it proves the bounds are ordered. This includes signed
versus unsigned min for nonnegative operands, sign replication for the
smallest signed clip, and the signed-positive predicate for a one-bit
unsigned result. These extra TableGen rules are counted in PatternGen's
statistics and the aggregated report. The rewrite is restricted to RV32
register results and targets that preserve signed min/max operations.

The unsigned immediate encodings 0 and 1 return zero for every input. LLVM
eliminates their register operand, so they do not produce useful extracted
instruction patterns. Semantic checks cover both encodings, and their
codegen checks require a constant-zero result.

Each clip instruction has its own codegen test file. The tests cover every
immediate value, both clamp orders, and negative checks for the unmasked
register expression. They run with SelectionDAG and GlobalISel at `-O0` and
`-O3`, with fallback disabled. To check the extracted descriptions and the
bounds proof independently:

```sh
python3 examples/corev/check_clip_semantics.py \
  "$DEST/.seal5/temp/XCoreVAlu/XCoreVAlu" \
  --opt "$DEST/.seal5/build/release_assertions/bin/opt" \
  --pattern-gen "$DEST/.seal5/build/release_assertions/bin/pattern-gen"
```

The checker covers 723 boundary cases, two constant-specialization skips, and
four bounds-proof extraction checks. For the latter checks it removes the
bound mask in temporary copies and requires PatternGen to stop emitting the
interchangeable clamp-order rules.

The four clip files cover 132 functions across four selector/optimization
configurations: 512 positive clip selections, eight constant-zero checks, and
eight negative checks. The extracted clip rule counts are 66 (`CV_CLIP`),
91 (`CV_CLIPU`), two (`CV_CLIPR`), and three (`CV_CLIPUR`); multiple equivalent
source trees can select the same encoding. These totals count emitted rules,
not just immediate values.


## Rounded normalization

The four immediate rounded add/subtract descriptions and eight rounded
multiply/MAC descriptions use `[[auto_unroll_imm]]`. Each immediate value
0–31 is extracted separately. The ALU descriptions express the rounding
term as `(one << shift) >> 1`, with `one` declared `unsigned<32>`. This makes
zero rounding explicit at count zero and keeps the intermediate word-sized
when the count is a five-bit register slice. Arithmetic wraps to 32 bits
before the final arithmetic or logical right shift.

The CoreDSL writer preserves the declared type of literal shift operands.
PatternGen also emits both wrapping rounded-subtraction trees,
`((a + rounding) - b) >> shift` and `((a - b) + rounding) >> shift`, for
specialized counts. This prevents missed matches when IR optimization moves
the rounding addition across the subtraction. The new rules are ordinary
TableGen patterns and are included in the extraction metrics.

At count zero, some signed/unsigned and rounded/unrounded encodings have
identical source patterns. Generated zero-count checks accept either encoding
only when complete extracted trees, predicates, output constraints, and
pure instruction flags agree. Nonzero checks still require the requested
instruction. Both rules remain counted; no per-pattern import or match count
is inferred from this equivalence. Assembler and intrinsic tests continue to
check the individual encodings.

The 16 rounded instruction files exercise all 32 immediate values for the
12 immediate forms, both subtraction trees, and the four register-controlled
forms with both selectors at `-O0` and `-O3`, with fallback disabled: 1,800
function/configuration checks. Independent constant folding verifies 3,456
rounded ALU cases and 3,216 MAC cases, including overflow, negative values,
zero counts, count 31, and high bits in register-controlled counts.

```sh
python examples/corev/check_alu_normalization_semantics.py \
  "$DEST/.seal5/temp/XCoreVAlu/XCoreVAlu" \
  --opt "$DEST/.seal5/build/release_assertions/bin/opt"
python examples/corev/check_mac_semantics.py \
  "$DEST/.seal5/temp/XCoreVMac/XCoreVMac" \
  --opt "$DEST/.seal5/build/release_assertions/bin/opt"
```

## Packed comparison patterns

The LLVM 22 configuration enables `FeatureGPR32VCmp` through the generated
XCoreVSimd feature. Its `gpr32v-cmp` switch preserves byte and halfword integer
comparisons during legalization. Disable it explicitly to use scalar expansion:
`-mattr=+m,+xcorevsimd,-gpr32v-cmp`. LLVM 23 remains a separate follow-up.

All 60 register, scalar-broadcast, and immediate-broadcast comparison forms now
extract vector patterns. Byte rules use `v4i8` and `GPR32V4`; halfword rules use
`v2i16` and `GPR32V2`. A broadcast operand remains a scalar GPR or immediate
inside `splat_vector`, allowing the complete comparison to select one CORE-V
instruction. These packed values occupy ordinary 32-bit integer registers.
Standalone broadcasts have a scalar shift/OR fallback.

PatternGen reconstructs a vector comparison when SLP has packed only the
scalar boolean results. It combines contiguous nonvolatile, nonatomic lane
loads only when no intervening side effect can change the reads, and recognizes
uniform broadcast operands. GlobalISel preserves comparisons whose boolean
results are sign-extended to full lane masks; other mask uses retain scalar
fallbacks. Both operand orders receive an equivalent TableGen rule, and both
rules contribute to the pattern statistics.

The cost model assigns one instruction to a legal packed comparison and zero
additional cost to its sign extension into an all-ones/zero lane mask.
The packed-vector/i32 register views and insertion into lane zero of poison
cost zero. A lane-zero broadcast used only by a comparison and full-lane mask
extension costs zero; a standalone or shared byte/halfword broadcast costs
seven/three scalar instructions, matching the shift/OR fallback. Queries without
an instruction context retain this standalone estimate. Other shuffles and
packing retain conservative costs. These are instruction-count estimates, not
measured cycle costs, and the comparison-specific costs require `gpr32v-cmp`.
SelectionDAG preprocessing keeps these broadcasts out of RVV lowering.
The generic machine verifier now accepts fixed-vector splats and retains its
checks for invalid destinations, vector sources, and undersized scalar sources.

The 40 per-instruction codegen files cover register and scalar-broadcast
comparisons with both selectors. Scalar-broadcast checks require selection at
both `-O0` and `-O3`, with GlobalISel fallback disabled. Additional checks cover
standalone/shared broadcasts, disabling the capability, and comparison/mask
costs. Four C array-threshold tests additionally run the normal `-O3` vectorizer
without forced widths. Signed/unsigned bytes vectorize at width four and
halfwords at width two, with scalar tails. `restrict` and explicit four-byte
alignment are caller contracts; these tests do not assume unaligned word loads.
Both selectors emit packed comparisons: GlobalISel selects scalar-broadcast
forms, while SelectionDAG currently hoists the broadcast and selects an
equivalent register comparison. The latter still pays the broadcast setup cost.
The loops demonstrate compiler decisions and selection, not a measured speedup
or execution on CORE-V hardware.
Independent evaluation checks all 120 extracted comparison rules against lane
semantics: 87,760 cases, including every six-bit immediate encoding. Another
5,940 scalar comparison cases verify register-lane offsets with the capability
disabled. Widened plain register loads previously lost nonzero byte offsets,
which could incorrectly reuse lane zero in signed expressions.

```sh
python examples/corev/check_simd_comparison_semantics.py \
  "$DEST/.seal5/temp/XCoreVSimd/XCoreVSimd" \
  --pattern-gen "$DEST/.seal5/build/release_assertions/bin/pattern-gen"
```

# Full CORE-V example (LLVM 22)

Run from the repository root with the Python environment activated:

```sh
LLVM_REF=llvmorg-22.1.8 SEAL5_NUM_THREADS=1 CCACHE=1 \
BUILD_CONFIG=release_assertions IGNORE_ERROR=1 TEST=1 INSTALL=0 DEPLOY=0 EXPORT=0 \
DEST=/tmp/seal5_llvm_corev_llvm22 python examples/corev_demo.py
```

The example includes all 311 instructions from XCoreVAlu, XCoreVBitmanip,
XCoreVMac, XCoreVSimd, XCoreVMem and XCoreVBranchImmediate. Hardware loops
are not included. The LLVM 22 configuration selects the packed-SIMD
PatternGen branch and enables memory normalization and immediate-branch
patterns. It uses ordinary TableGen patterns, without direct GISel tables.

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
| Checked-in codegen tests | 48 | 20 |
| Generated pattern codegen tests | 46 | 59 |

The checked-in total is **587/607 passing**. Assembler tests cover all 311
instructions and compare each sample encoding with LLVM's native CORE-V
assembler. The new codegen tests for both immediate branches, all eight
ordinary register-offset loads/stores, and four packed add/sub operations
pass. Those tests exercise both SelectionDAG and GlobalISel, with GlobalISel
fallback disabled.

The remaining checked-in failures concern rounded normalization and clipping. One obsolete
unsigned multiply test used an arithmetic right shift; it now uses a logical
right shift. Generated-test failures include equivalent-instruction choices
(such as byte versus halfword bitwise operations) and genuine missing
matches, including dot products and scalar-broadcast comparisons. A failed
exact-instruction check therefore does not by itself prove incorrect code.
All failing checks remain enabled, without XFAIL annotations.

`IGNORE_ERROR=1` lets the experimental run finish and collect reports despite
these failures. Omit it to make the TEST stage stop on a failing check. This
is not yet a fully passing pattern-selection suite.

| Instruction set | Instructions | Extracted patterns | Failed extraction | Skipped |
| --- | ---: | ---: | ---: | ---: |
| ALU | 31 | 31 | 0 | 0 |
| Bit manipulation | 16 | 10 | 3 | 3 |
| Immediate branches | 2 | 2 | 0 | 0 |
| MAC | 18 | 142 | 0 | 0 |
| Memory | 24 | 8 | 0 | 16 |
| SIMD | 220 | 96 | 124 | 0 |
| Total | 311 | 289 | 127 | 19 |

Extraction success does not establish importer acceptance or instruction
selection. The generated TableGen pattern files total 155,130 bytes in this
run. Reports retain separate extraction, import, and match fields; unavailable
validation counts remain unknown.

MAC behavior follows the 32-bit truncation before normalization in the
[CV32E40P multiplier RTL](https://github.com/openhwgroup/cv32e40p/blob/master/rtl/cv32e40p_mult.sv).
The rounding term is zero for normalization amount zero. The extracted MAC
IR passes 712 constant-folding checks, covering all 32 normalization amounts
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
311 instructions. Specialization is intentionally limited to these four
instructions rather than every small immediate in the example.

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

Immediate specialization additionally exposes four generated wrapper-test
failures, increasing the generated suite from 101 to 105 files. Those wrappers
load halfwords through pointers; load folding removes the explicit extraction
operations and the resulting code uses ordinary multiply instructions. These
checks remain enabled. They are distinct from the passing scalar-register
patterns above. Generated-test labels now identify each specialized function
and check the shared target instruction, and diagnostic output is captured
separately so statistics cannot interrupt a pattern record.

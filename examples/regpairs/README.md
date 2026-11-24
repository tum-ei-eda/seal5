# RV32 even/odd register pairs

This example implements a small custom ISA on LLVM 22 and LLVM 23:

| Instruction | Operation on a 64-bit register pair |
|---|---|
| `pair.add64 rd, rs1, rs2` | Addition modulo 2^64, including carry between words |
| `pair.add.2x32 rd, rs1, rs2` | Two independent additions modulo 2^32 |
| `pair.sub64 rd, rs1, rs2` | Subtraction modulo 2^64, including borrow between words |
| `pair.sub.2x32 rd, rs1, rs2` | Two independent subtractions modulo 2^32 |
| `pair.mul.2x32 rd, rs1, rs2` | Two low-word products modulo 2^32 |
| `pair.xor64 rd, rs1, rs2` | Bitwise XOR |
| `pair.and64 rd, rs1, rs2` | Bitwise AND |
| `pair.slli64 rd, rs1, shamt` | Logical left shift |
| `pair.srli64 rd, rs1, shamt` | Logical right shift |
| `pair.srai64 rd, rs1, shamt` | Arithmetic right shift |
| `pair.rori64 rd, rs1, shamt` | Rotate right |

A pair is written using its **even** register: `x10` means the low word in
`x10` and the high word in `x11`. Legal register operands are `x0, x2, …, x30`.
The `x0` pair reads as 64-bit zero and discards writes to both words; it never
reads or writes `x1`. This follows LLVM's existing `GPRPair` convention, rather
than treating `x0:x1` as an ordinary pair. Sources are read before either
output word is written, including when destination and source pairs overlap.
Odd register encodings are reserved and rejected by the assembler/decoder.
The instructions use custom-0 and must not be enabled together with a different
custom-0 ISA with overlapping encodings.

The example declares the pair view explicitly:

```c
architectural_state {
  register unsigned<64> XP[32] [[is_regpair]];
}
// rs1 is the encoded five-bit register ID, not a pair number.
a = XP[rs1];
```

`[[is_regpair]]` makes this a view of the existing RV32 `X` bank, rather than
independent architectural storage. There are sixteen pairs, but the view accepts
encoded register IDs: when `rs1` is 6, `XP[rs1]` means the x6/x7 pair. The 32
positions describe the encoded index space, with only the sixteen even positions
denoting legal pair starts. No implicit shift or masking is applied;
source code must not add its own `>> 1`. The marker declares an even/odd view,
not thirty-two independent 64-bit registers.
Operand classification follows the declaration automatically, without YAML
`register_pairs` mappings or matching concatenations.

The examples check the original IDs before accessing the view:

```c
if (((rd | rs1 | rs2) & 1) != 0) {
  raise(0, RV_CAUSE_ILLEGAL_INSTRUCTION);
} else {
  // Read sources, compute result, then write XP[rd].
}
```

An index conversion alone cannot implement this exception: it loses the odd bit.
The full architectural export retains these checks and lowers XP accesses to
shared `X` storage. Reads of pair zero produce zero; writes discard both words.
Stores evaluate their RHS once before either word is modified. The declaration
itself does not insert runtime traps; put legality checks in the behavior.

For standard CoreDSL output, including the original traps and expanded shared
storage, use:

```sh
python -m seal5.backends.coredsl2.writer /path/to/RegPairs.seal5model \
  --architectural -o /tmp/RegPairs.architectural.core_desc
```

The snapshot used for this export is taken before compiler constraint extraction
can replace exception calls with operand preconditions.

Compiler operands use LLVM's even-only `GPRPair` class. During reduced emission
and call analysis, SEAL5 specializes parity checks only when their result follows
from that class; the architectural behavior stays intact. Unknown checks are not
removed. Reduced PatternGen `XP[rs1]` is a symbolic operand reference, with no
runtime array indexing.

The two source examples implement the same eleven instructions:

| Style | Source | Selection |
|---|---|---|
| Explicit view | `cdsl/RegPairs.core_desc` | `PAIR_STYLE=explicit` (default) |
| Inferred pairs | `cdsl/inferred/RegPairs.core_desc` | `PAIR_STYLE=inferred` |

The inferred example uses ordinary architectural registers:

```c
unsigned<64> a = X[rs1 + 1] :: X[rs1];
// Compute a 64-bit local result before writing either word.
X[rd] = result[31:0];
X[rd + 1] = result[63:32];
```

SEAL5 infers pair operands from complete high/low concatenations and adjacent
writes of the two halves of the same 64-bit local. Both examples need no YAML
pair mappings. The optional `collect_register_operands.register_pairs` mapping
remains available for operands whose usage does not establish a complete pair.
Emission normalizes the inferred form to the same XP operand.
Individual words become slices, and adjacent writes of a single evaluated local
result can become one pair store. Mismatched/reversed pairs and alias-sensitive
writes are not combined. Pair views and pair metadata currently require RV32.

## Run the example

From a SEAL5 Python environment, with the usual build prerequisites:

```sh
LLVM_REF=llvmorg-23.1.3 BUILD_CONFIG=release_assertions \
  DEST=/tmp/seal5_llvm_regpairs INSTALL=0 DEPLOY=0 EXPORT=0 \
  python examples/regpairs_demo.py
```

For LLVM 22, replace `LLVM_REF=llvmorg-23.1.3` with
`LLVM_REF=llvmorg-22.1.8`; both source styles are supported.

To run the inferred source through the same flow and tests, add
`PAIR_STYLE=inferred` to the command above (use a separate `DEST` for each style).

`examples/gpr32_demo.py` is a compatibility entry point to this example.
The default flow builds assembler/disassembler, intrinsics, builtins and generated
SelectionDAG patterns, then runs the `.test-*` source tests. Generic PatternGen
test generation is disabled for this example because it assumes XLEN operands
and GlobalISel; dedicated pair tests and the execution runner cover this path.

The example selects the matching CoreDSL2LLVM dependency branch and versioned
patches for XP parsing, pair extraction, and backend legalization. LLVM 22 uses
`llvm-22.1.8`; LLVM 23 uses `llvm-23.1.3-packed-simd`. The LLVM 22 adapter adds
the pair-vector memory, bitcast, and ABI handling that the LLVM 23 backend
already provides. Scalar `i64` remains illegal on RV32 in both versions.
The generated extension implies separate arithmetic capabilities:

| Internal feature | Legal operations |
|---|---|
| `seal5-regpair32` | Shared `<2 x i32>` register-pair representation and word transfers |
| `seal5-regpair32-add` | Scalar `i64` ADD and `<2 x i32>` ADD |
| `seal5-regpair32-sub` | Scalar `i64` SUB and `<2 x i32>` SUB |
| `seal5-regpair32-mul` | `<2 x i32>` MUL; scalar `i64` multiplication still expands |

Each arithmetic feature implies the shared representation. Selection additionally
requires `xregpairs`; enabling an internal feature alone cannot emit these custom
instructions. LLVM clears a parent feature when an implied capability is disabled,
so `+xregpairs,-seal5-regpair32-sub` disables the parent ISA and uses scalar fallback
for all five operations. These are lowering capabilities, not separately specified
architectural subextensions. Neither P nor RVV is enabled. A feature-bit capacity patch is applied when needed.
Both behavior passes retain `no_extend: false`.

## C builtins and LLVM intrinsics

```c
#include <stdint.h>
uint64_t sum(uint64_t a, uint64_t b) {
  return __builtin_riscv_xregpairs_add64(a, b);
}
uint64_t lanes(uint64_t a, uint64_t b) {
  return __builtin_riscv_xregpairs_add_2x32(a, b);
}
```

Compile using `clang --target=riscv32 -march=rv32imxregpairs -mabi=ilp32`.
The additional builtins are `__builtin_riscv_xregpairs_sub64`,
`__builtin_riscv_xregpairs_sub_2x32`, and `__builtin_riscv_xregpairs_mul_2x32`,
all with the same two-argument `uint64_t` interface.
The packed builtin uses bits 31:0 and 63:32 as separate unsigned lanes.
It has a scalar bit-container interface, rather than a vector C ABI.

The corresponding LLVM declarations are:

```llvm
declare i64 @llvm.riscv.xregpairs.add64(i64, i64)
declare i64 @llvm.riscv.xregpairs.add.2x32(i64, i64)
declare i64 @llvm.riscv.xregpairs.sub64(i64, i64)
declare i64 @llvm.riscv.xregpairs.sub.2x32(i64, i64)
declare i64 @llvm.riscv.xregpairs.mul.2x32(i64, i64)
```

LLVM's normal ILP32 calling convention is retained. Arguments may arrive in
odd/even ABI register combinations or on the stack; register allocation and
copies place instruction operands in even/odd physical pairs. Pair values can
be copied, spilled and restored using the existing backend machinery.

RV32 `i64` remains an illegal scalar SelectionDAG type. An ordinary generated
`Pat` returning `i64` cannot solve this. The example's target lowering splits
the scalar inputs, builds existing `BuildGPRPair` nodes, emits the custom
instruction and reconstructs the scalar result from its two subregisters.
SEAL5 suppresses the invalid scalar pair intrinsic pattern; **another scalar
pair instruction needs its own lowering adapter**, not just a YAML intrinsic
entry. The example also legalizes `<2 x i32>` addition, subtraction and multiplication for generated vector patterns.
The implemented compiler path is SelectionDAG; GlobalISel support is not
provided by this example.

## Semantic and execution checks

After extracting the behavior, run:

```sh
python examples/regpairs/check_semantics.py /path/to/extracted/XRegPairs \
  --opt /path/to/build/bin/opt --output /tmp/regpairs-semantics
```

This compares all five generated IR implementations against 1,525 independent
boundary/random arithmetic cases. Outputs are separate temporary snapshots;
physical source/destination overlap is checked separately by execution.

The execution runner requires Spike headers matching the Spike executable and
a baseline RV32-capable GCC toolchain:

```sh
python examples/regpairs/execute.py --bin /path/to/build/bin \
  --gcc /path/to/riscv64-unknown-elf-gcc --spike /path/to/spike \
  --spike-source /path/to/riscv-isa-sim --spike-build /path/to/spike-build \
  --output /tmp/regpairs-execution
```

It builds an independent Spike extension and checks Clang builtins and LLVM
IR intrinsics, ordinary scalar arithmetic and explicit vector arithmetic at O0/O2/O3
against baseline GCC arithmetic. Cases include
boundary values, 4,096 random inputs, an odd ABI argument position, 128
register-pressure cases, pair overlap, `x0`, and preservation of `x1`.
The runtime reuses only boot/link scaffolding from `packed_simd/runtime`.
It is a functional validation, not a timing or performance benchmark.

## Pattern extraction and vectorization investigation

Record reproducible probes from a transformed SEAL5 model:

```sh
python examples/regpairs/probe.py --bin /path/to/build/bin \
  --model /path/to/.seal5/models/RegPairs.seal5model \
  --output /tmp/regpairs-probe
```

The probe writes semantic IR, extraction diagnostics and optimized IR/assembly
for ordinary and explicitly width-requested C loops. It records failures as
results rather than silently substituting hand-written patterns.

Current findings:

- All eleven descriptions produce generated patterns. Pair functions are extracted
  before GlobalISel legalization splits the output into word stores. Ordinary
  PatternGen functions retain their existing extraction pipeline.
- ADD64 and SUB64 map to target pair nodes whose result has the existing untyped
  `GPRPair` representation. RV32 scalar `i64` stays illegal, preserving the
  normal ILP32 ABI. Ordinary C `uint64_t` addition/subtraction selects `pair.add64`/`pair.sub64`.
- The packed semantic expression is recognized only when it proves two
  complete, independent 32-bit lane operations with matching inputs. It becomes
  a `<2 x i32>` ADD, SUB or MUL and selects the corresponding instruction.
  Subtraction preserves input order; multiplication recognizes the masked
  wide-product form introduced by InstCombine.
  No instruction-name matching is used for this recognition.
- Explicit vector arithmetic, pair construction/extraction and split memory
  transfers work with only the custom extension. Unsupported vector operations
  expand to scalar instructions. Generated patterns require both the ISA and
  the internal legalization capability.
- Automatic loop vectorization remains deferred. The ordinary and explicitly
  width-requested loops remain scalar. A useful vectorizer cost model must
  describe two-word transfers, unsupported operations, packing and increased
  GPR pressure; the narrow lane-cost fixes here prevent RVV assumptions but do
  not provide that full model.
- SelectionDAG is supported. Pair GlobalISel code generation and GlobalISel
  table extraction are not implemented; no-fallback probes report failure.

The scalar pair nodes support register/register ADD64, SUB64, XOR64 and AND64,
plus immediate left/right shifts and rotate-right. Shift counts are six-bit
constants in 0–63. Rotate-left constants select rotate-right with the complementary
count. Variable-count C operations expand using ordinary RV32 instructions.
The internal `seal5-regpair32-logic` and `seal5-regpair32-shift` capabilities
gate automatic selection of the new operations. Disabling either required
capability also clears the parent ISA feature in LLVM. For an add-only benchmark
while keeping the ISA enabled, use `-mllvm -riscv-seal5-regpair-bitops=false`;
explicit builtins remain available. Further
scalar pair operations need explicit lowering support; further packed element
sizes need their own legalization and semantic recognition. These patches are
an example implementation rather than generic support for every pair operation.

Check positive extraction and rejection of mismatched/reversed lanes with:

```sh
python examples/regpairs/check_extraction.py /path/to/reduced/XRegPairs \
  --pattern-gen /path/to/build/bin/pattern-gen --output /tmp/regpairs-extraction
```

Upstream reference:
[LLVM RV32 P-extension register-pair support](https://github.com/llvm/llvm-project/commit/5e4a21a1b9464ac483daf47deb2d6e4edb8228fe).
See [validation results](results/validation.md) for what was actually tested.

## SHA-512 benchmark

`benchmark_sha512.py` extracts the unchanged compression function and constants
from Mbed TLS 2.28.10 `library/sha512.c`. Supply that file from the
[`mbedtls-2.28.10` tag](https://github.com/Mbed-TLS/mbedtls/blob/mbedtls-2.28.10/library/sha512.c).
The runner compares RV32IM, add-only pairs, and full pairs at O2/O3, with both
normal and `MBEDTLS_SHA512_SMALLER` implementations. Each run verifies the
SHA-512 digest of `abc`. Only the compression call is measured; the independent
GCC-compiled harness and zeroization routine are shared across variants.

```sh
python examples/regpairs/benchmark_sha512.py --bin /path/to/build/bin \
  --gcc /path/to/riscv64-unknown-elf-gcc --spike /path/to/spike \
  --pair-plugin /path/to/execution/libseal5-regpairs.so \
  --marker-plugin /path/to/libseal5-packed.so \
  --source /path/to/mbedtls/library/sha512.c --output /tmp/pair-sha512
```

The marker plugin is built by `examples/packed_simd/execute.py`; the pair plugin
is built by this example's `execute.py`. Results include the source SHA-256,
per-variant logs and disassembly. Spike reports retired instructions; these
measurements do not establish hardware cycle speedups or instruction latency.

A [comparison with scalar RV32 alternatives](results/scalar32-comparison.md)
measures generic funnel shifts/ADD3 and specialized RV32 SHA-512 instructions
without register pairs. These scalar variants use explicit C/IR instruction
insertion; they do not yet have automatic Seal5 selection.

The [aha-mont64 follow-up](results/mont64.md) measures the expanded extension,
profiles the remaining hotspots, and fixes automatic selection of pair masks
and shifts that are cheaper as scalar word operations. The ISA and explicit
builtin coverage remain the same; automatic shifts with counts >=32 and AND
masks with a zero word use scalar legalization to preserve known bits.

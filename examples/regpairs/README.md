# RV32 even/odd register pairs

This example implements a small custom ISA on LLVM 23:

| Instruction | Operation on a 64-bit register pair |
|---|---|
| `pair.add64 rd, rs1, rs2` | Addition modulo 2^64, including carry between words |
| `pair.add.2x32 rd, rs1, rs2` | Two independent additions modulo 2^32 |
| `pair.sub64 rd, rs1, rs2` | Subtraction modulo 2^64, including borrow between words |
| `pair.sub.2x32 rd, rs1, rs2` | Two independent subtractions modulo 2^32 |
| `pair.mul.2x32 rd, rs1, rs2` | Two low-word products modulo 2^32 |

A pair is written using its **even** register: `x10` means the low word in
`x10` and the high word in `x11`. Legal register operands are `x0, x2, …, x30`.
The `x0` pair reads as 64-bit zero and discards writes to both words; it never
reads or writes `x1`. This follows LLVM's existing `GPRPair` convention, rather
than treating `x0:x1` as an ordinary pair. Sources are read before either
output word is written, including when destination and source pairs overlap.
Odd register encodings are reserved and rejected by the assembler/decoder.
The instructions use custom-0 and must not be enabled together with a different
custom-0 ISA with overlapping encodings.

The CoreDSL behavior describes the actual two 32-bit `X` registers. The YAML
`collect_register_operands.register_pairs` mapping identifies which fields
represent complete pairs. No independent 64-bit architectural register bank
is introduced. `X[operand]` and `X[operand + 1]` then map to one LLVM `GPRPair`
operand with a 64-bit semantic snapshot. An emission-only normalization pass
rewrites `X[rs1 + 1] :: X[rs1]` to `XP[rs1]`. Individual words become slices of
`XP`, and adjacent writes of the low/high halves of one evaluated 64-bit local
result become one `XP[rd] = result` assignment. Mismatched/reversed pairs and
alias-sensitive writes are not combined. The full architectural description
and shared `X` bank are preserved; `XP` exists only in reduced PatternGen input.
Pair metadata is currently RV32-only;
unsupported word offsets are rejected. As with other register-class metadata,
it also defines the legal operand set of the description.

## Run the example

From a SEAL5 Python environment, with the usual build prerequisites:

```sh
LLVM_REF=llvmorg-23.1.3 BUILD_CONFIG=release_assertions \
  DEST=/tmp/seal5_llvm_regpairs INSTALL=0 DEPLOY=0 EXPORT=0 \
  python examples/regpairs_demo.py
```

`examples/gpr32_demo.py` is a compatibility entry point to this example.
The default flow builds assembler/disassembler, intrinsics, builtins and generated
SelectionDAG patterns, then runs the `.test-*` source tests. Generic PatternGen
test generation is disabled for this example because it assumes XLEN operands
and GlobalISel; dedicated pair tests and the execution runner cover this path.

The example uses the LLVM 23 CoreDSL2LLVM dependency branch with local patches
for XP parsing, pair extraction, and narrowly gated backend legalization.
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

- All five descriptions produce generated patterns. Pair functions are extracted
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

The scalar pair nodes currently support register/register ADD64 and SUB64. Further
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

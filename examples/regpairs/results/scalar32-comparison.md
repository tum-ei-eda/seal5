# SHA-512: alternatives without register pairs

Measured with the same LLVM 23 validation compiler, Mbed TLS 2.28.10 SHA-512
compression function, GCC baseline harness and Spike measurement marker as the
original pair benchmark. All 28 runs pass the SHA-512 `abc` digest check. O2 and
O3 give identical instruction counts for each variant. The baseline and regpair
counts exactly reproduce the earlier results.

These are retired instructions, not measured hardware cycles. Custom instruction
latencies, register-file ports, implementation area and energy are not evaluated.

| ISA / selection | Normal instructions | Reduction | Smaller instructions | Reduction |
|---|---:|---:|---:|---:|
| RV32IM baseline | 14,293 | — | 17,217 | — |
| RV32IM + Zbb, ordinary C | 14,304 | -0.1% | 17,217 | 0.0% |
| Scalar funnel shifts | 11,366 | 20.5% | 14,115 | 18.0% |
| Scalar funnel shifts + ADD3 | 10,606 | 25.8% | 13,355 | 22.4% |
| RV32 Zknh SHA-512 instructions | 8,802 | 38.4% | 11,555 | 32.9% |
| RV32 Zknh SHA-512 + scalar ADD3 | 8,322 | 41.8% | 11,242 | 34.7% |
| Full regpair extension, ordinary C | 7,989 | 44.1% | 10,427 | 39.4% |

## Generic scalar extension

Every custom scalar instruction reads explicitly named individual RV32 registers
and writes one 32-bit register. There is no even/odd restriction, implicit next
register, pair register class, or paired output. Encodings in the benchmark use
odd registers as well as even registers.

- Funnel shift: `rd = (rs1 >> n) | (rs2 << (32 - n))`, with the zero-count case
  defined as `rd = rs1`. The immediate is 0–31. Two instructions compute a full
  64-bit rotation; counts above 31 interchange the input halves.
- ADD3: `rd = (rs1 + rs2 + rs3) mod 2^32`. A 64-bit addition uses an ordinary
  low-word ADD, SLTU for carry, and ADD3 for the high word. Carry is an explicit
  register value, with no flags or hidden state. ADD3 requires three source
  register reads, which should be included in a hardware cost comparison.

XOR32, AND32 and logical/arithmetic shifts are already available in RV32I, so
adding identical custom instructions would not reduce instruction count.
A 32-bit rotate alone does not move bits between the two words of a 64-bit
value; the Zbb result here does not approach the generic regpair improvement.

This matching generic scalar prototype recovers substantial savings, but less
than the regpair extension. Regpairs still compute both halves of XOR/AND,
rotations and additions in one instruction.

## More specialized RV32 alternative

Zknh supplies RV32 SHA-512 sigma/sum instructions with ordinary scalar register
operands. Two instructions calculate both halves of a sigma/sum transformation,
combining several shifts and XORs per output. See the
[RISC-V scalar cryptography specification](https://docs.riscv.org/reference/isa/unpriv/scalar-crypto.html).

This specialization reaches reductions close to the regpair result, especially
for the normal implementation, without register pairs. It is more specific to
SHA-512 than the generic pair operations and does not establish the same benefit
for arbitrary 64-bit workloads.

## Selection and reproducibility

The scalar prototypes explicitly replace the rotation or sigma/sum macros with
inline-assembly helpers. ADD3 variants additionally replace scalar i64 ADDs in
optimized LLVM IR with a split helper before code generation. This demonstrates
ISA feasibility; automatic extraction/selection through Seal5 has not been
implemented for these prototypes. The SHA algorithm and round constants are
retained, and the unchanged GCC harness verifies every result. The regpair
variant uses ordinary C with existing automatic SelectionDAG selection.

The custom scalar instructions use custom-0 encodings that overlap the pair
example. The runner loads one corresponding Spike extension at a time. Scalar
runs compile without `xregpairs` and do not load the pair plugin.

Build `benchmark/scalar32-spike.cc` as a shared library using the same Spike
headers as `execute.py`, for example:

```sh
c++ -std=c++17 -fPIC -shared -I/path/to/spike/riscv -I/path/to/spike \
  -I/path/to/spike-build examples/regpairs/benchmark/scalar32-spike.cc \
  -o /tmp/libseal5-scalar32.so
python examples/regpairs/benchmark_scalar32.py --bin /path/to/llvm/bin \
  --gcc /path/to/riscv64-unknown-elf-gcc --spike /path/to/spike-build/spike \
  --pair-plugin /path/to/libseal5-regpairs.so --scalar-plugin /tmp/libseal5-scalar32.so \
  --marker-plugin /path/to/libseal5-packed.so \
  --source /path/to/mbedtls/library/sha512.c --output /tmp/scalar32-comparison
```

[Raw results](sha512-scalar32-llvm23.json) include the upstream source hash,
compiler version, per-variant digest status and static instruction counts.
Commands, IR, assembly, binaries and execution logs for this run are under
`/tmp/seal5-scalar32-comparison/final`.

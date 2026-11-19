# Merged-main validation

The CDSL submodule is upstream main `56b66cfea193b28cd88ea89a684469ef76fa31cc`.
LLVM 22 and ETISS were regenerated from that source, with the runtime adapter
and generator fixes described in [the regeneration notes](../review/README.md).
[Model hashes](main-model-manifest.json) identify the tested ETISS input.

- Python: 113 passed.
- Source assembly, intrinsics, builtins and codegen: 651 passed, 2 unsupported
  (CLB is disabled upstream), zero failures.
- Native ETISS execution: [4,592 raw instruction checks](main-instruction-checks.txt),
  zero failures, including clipping, operand aliasing and rotate cases.
- Extracted IR semantics: 40,800 dot-product checks, 87,760 packed comparison
  checks, 5,940 scalar comparison checks, 723 clip cases, 3,456 rounded ALU
  cases and 3,216 MAC cases passed. Four clamp bounds proofs and two constant
  specialization skips passed. Rotate extraction accepts the identity guard
  and rejects wrong-guard/wrong-value variants.
- Pattern extraction: 183 descriptions succeeded, 26 were skipped and 101
  failed out of 310. [Raw per-extension metrics](main-pattern-metrics.json)
  preserve the instruction lists. These are extraction counts, not total ISA
  support counts; unsupported automatic patterns can still use intrinsics.
- Generated selection tests: 124 passed, 14 exact-opcode checks failed.
  Eight comparison tests select the equivalent reversed GT/GE operation with
  swapped operands. Six miss the expected opcode: AND_H, OR_H, XOR_H, AVG_B,
  AVG_H and AVGU_H. These remain performance opportunities. Signed immediate
  EXTRACT extraction also needs s33 sign-extension legalization. EXTRACTUR works.

The immediate branch guard is simplified only in reduced pattern input where
its collected constraint proves alignment; the stored executable behavior keeps
the guard. ROR gains an equivalent plain rotate pattern after checking the
zero-count arm, source value, count and modulo-32 mask. Scalar bitwise patterns
with erased vector bitcasts are rejected before TableGen.

The benchmark uses an independently checked instruction counter. ETISS model
cycles assume CPI=1 and must not be presented as hardware timing or speedup.

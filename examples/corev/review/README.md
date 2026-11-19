# CORE-V CoreDSL review and ETISS regeneration

## Merged upstream main validation (2026-11-19)

The current integration uses upstream main `56b66cfea193b28cd88ea89a684469ef76fa31cc`,
after both PRs were merged. The branch and review snapshots below are historical.
LLVM and ETISS were regenerated from this merged source. ETISS still uses the
runtime adapter and generator corrections documented below; its strict source
and behavior checks and all 4,592 native instruction checks pass.
See `../results/main-model-manifest.json` for the exact model input hashes.

LLVM integration retains SLE/SLEU assembly naming, keeps disabled CLB unsupported,
and preserves guarded immediate-branch semantics. Reduced branch patterns omit
an alignment guard only when the instruction specialization proves it false.
The rotate matcher emits an unconditional rotate only after proving the
zero-count arm returns the same value with the same modulo-32 count.
Malformed scalar bitwise patterns containing vector operands are rejected.


Reviewed PR #2 (`fixes-2026`, `5aa2e308b59b1ab0ed6c3460f8f92559f775f706`)
against PR #3 (`restore-xcorev-llvm22`, `9ad25f4e8d03494ce697146dece947179bfaf3d3`).
The tested integration is commit `4c23875729060b8b967fa4039ce142a57aef1a7d`
on `review-integrated` in `corev-reviewed-integration.bundle`.
No upstream branch or pull request was modified.

## Restoration branch merge

Local merge commit `77377cb` on `restore-xcorev-llvm22` integrates main
`53a22ac` into restoration head `9ad25f4`. All six conflicting instruction
files are resolved. The merge retains the reviewed clipping and alias fixes,
main's six narrowed SIMD extraction/insertion selector encodings, and the
restoration's MAC encodings, normalization arithmetic and pattern factoring.
Immediate-branch alignment checks remain conditional on taking the branch.

The committed sources match the descriptions used for strict source/behavior
validation and successful native ETISS regeneration in
`/tmp/seal5-corev-restore-merge-validate`. The runtime adapter retains the
baseline JALR-mask and reservation-initializer corrections described below.
The regenerated runtime is `/tmp/seal5-corev-restore-merge-runtime-install`.
All 4,592 raw-instruction execution checks passed on this runtime, including
the clipping and alias regressions. The saved output is
`../results/restoration-merge-instruction-checks.txt`.
The submodule working tree is clean; no remote branch was modified by the
assistant. Earlier branch-state notes below are historical.

## Follow-up fixes on PR #2

The subsequent merge commit `b4c0b80` integrates main at `26138c3` and resolves
all five conflicting instruction files. The workspace submodule is on that
commit on local `fixes-2026`; nothing was pushed by the assistant. It preserves
the fixes below and main's conversion updates. The complete merged extension
descriptions now pass strict source/behavior validation with the tested runtime
adapter. The conflict and remaining-conversion notes below describe the earlier
review state, before this merge; the wider LLVM restoration remains separate.

The workspace submodule `examples/corev/cdsl` is now on local `fixes-2026`,
one commit ahead of its reviewed upstream head: `6d37665` (Fix SIMD input
aliasing, shuffle selectors and clipping bounds). This focused commit ports
the selector, aliasing and explicit-conversion corrections and fixes register
clipping bounds while preserving PR #2's imports, encodings and assembly
declarations. It includes the raw-instruction regression fixture in `tests/`.
It has not been pushed, and does not merge the LLVM restoration branch.

A newly generated model of the affected instruction groups passed strict
source/behavior validation, native ETISS generation and all 4,592 execution
checks. This validation covers the complete SIMD, bit manipulation and branch
groups plus the four clipping behaviors. Full PR #2 validation still reports
pre-existing failures in the remaining ALU/MAC behaviors; the broader reviewed
integration above addresses those. The main-branch conflict also remains to
be resolved during integration.

## Merge recommendation

Do not merge PR #2 unchanged. It also conflicts with the reviewed main head
`368250b75f91997b094eb353648a9894a14c1da0` in XCoreVSimd.core_desc.
The local integration resolves the PR #2 / PR #3 differences and fixes:

- CV_SHUFFLE_SCI_H reads `Imm6[16]` despite having a six-bit immediate. Use
  `Imm6[1]` for the upper halfword selector.
- Sequential SIMD lane writes can overwrite later source reads when destination
  and source registers alias. Snapshot inputs before writes in 17 shuffle,
  pack and rotated-subtract descriptions.
- Explicit signedness and width conversions are needed to pass strict source
  and behavior validation, including narrow selector arithmetic.
- Signed clipping must compare the source as signed. Retain the signed clip
  correction from PR #2 and the normalized clipping expressions from PR #3.
  In particular, `cv.clip(-1, 0)` must produce -1, not zero.

The integration retains PR #3's encoding and arithmetic corrections and PR #2's
expanded bit manipulation and branch fixes. The instruction semantics were
checked against the [CORE-V instruction manual](https://cv32e40p.readthedocs.io/en/latest/instruction_set_extensions.html).
CV_CLB remains disabled: the model contains 310 of 311 extension descriptions,
and this review does not establish correctness of every description.

PR #2 renames CV_SLET/CV_SLETU to CV_SLE/CV_SLEU. Before regenerating LLVM from
this candidate, update the corresponding `instr_name` entries in
`../cfg/XCoreVAlu.yml` and checks that reference the old identifiers. The
existing benchmark compiler uses the old identifiers with equivalent encodings;
it was deliberately held constant for the simulator comparison.

## Importing the candidate

The bundle contains complete history and both merge parents. From a clone:

```sh
git fetch /absolute/path/corev-reviewed-integration.bundle review-integrated:review-integrated
git switch review-integrated
```

`corev-integrated.patch` is the resulting tree diff against PR #3's reviewed
head; the bundle is preferable when preserving the integration history.

## Regeneration requirements

The local M2-ISA-R snapshot was based on commit 204131e plus its existing local
constant-folding changes. `m2isar-regeneration-fixes.patch` supplies two additional
fixes: InstructionSetGroup constructor arguments and dynamic PC substitution
when static scalar optimization is disabled. It is not a replacement for that
existing constant-folding work.

For exact reproduction, `m2isar-tested-snapshot.patch` contains the complete
Python-source delta from 204131e, including that constant-folding work and the
two regeneration fixes. Apply this combined patch instead of the smaller patch.
`m2isar-tested-snapshot-sha256.json` records the tested Python source hashes.

`runtime-baseline-width-fixes.patch` explicitly widens the JALR complement mask
and the reservation-address initializer in the baseline descriptions. With
literal-width constant folding, complementing the one-bit literal `0x1` before
widening yields zero and breaks indirect jumps. The shared workspace RVI
description also has the JALR mask correction applied.

Use the integrated XCoreV files together with the runtime adapter's baseline,
CSR and semihosting descriptions. The tested adapter is
`/tmp/seal5-corev-regenerated/top.core_desc`. Regenerate with:

```sh
env PYTHONPATH=/tmp/seal5-corev-reviewed-m2isar venv310/bin/python \
  -m m2isar.frontends.coredsl2.parser /tmp/seal5-corev-regenerated/top.core_desc \
  -I /tmp/seal5-corev-regenerated/rv_base --validate \
  --output /tmp/seal5-corev-regenerated/gen_model
env PYTHONPATH=/tmp/seal5-corev-reviewed-m2isar venv310/bin/python \
  -m m2isar.backends.etiss.writer \
  /tmp/seal5-corev-regenerated/gen_model/top.m2isarmodel \
  --separate --no-static-scalars --fill-mode auto
```

`--no-static-scalars` is required here: the static optimization emits undeclared
variables for nested BITREV loops. Validation stays enabled. The generated
architecture was built and installed against the existing ETISS ABI into
`/tmp/seal5-corev-etiss-runtime-install`; the old runtime was preserved.

## Validation

Strict source and behavior validation, architecture generation and native build
all passed. `../benchmark_runtime/instruction_checks.c` runs raw encoded
instructions independently of LLVM's CORE-V selection: **4,592 checks, zero
failures**. It covers every clip immediate, register clipping bounds, rotate,
bit operations, negative branch immediates and SIMD alias cases. This is focused
regression coverage, not exhaustive ISA certification.

The independent instruction counter's assembly self-test measures exactly 31
instructions, including ten custom additions. Embench is rerun with the LLVM
compiler unchanged, three repetitions per variant. See the saved results under
`../results/` for verification status, counts and the remaining compiler limit.
ETISS instruction/model-cycle counts are not hardware cycle measurements.

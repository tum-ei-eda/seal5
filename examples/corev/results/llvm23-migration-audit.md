# Initial LLVM 23 migration audit

This records the initial findings before fixes. The subsequent
[LLVM 23 validation](llvm23-validation.md) describes the implemented fixes,
additional issues found during the build and tests, and final results.

LLVM 23 is **not yet qualified for the full CORE-V example**. The first checks
found configuration correctness and patch integration blockers. This report
precedes implementation fixes, as requested. The LLVM 22 implementation and
build remain unchanged. This is not a completed LLVM 23 codegen or Embench run.

Inputs: merged CDSL `56b66cfea193b28cd88ea89a684469ef76fa31cc`; local LLVM
23.1.3 packed-SIMD dependency `f3e4c5705c2da4ecadc2babeae356e2960220293`.
The [machine-readable evidence](llvm23-migration-audit.json) contains the
configuration comparison and sequential patch application diagnostics.
Scratch artifacts and command output are in `/tmp/seal5-corev-llvm23-audit`.
No remote branch was fetched or modified during this audit.

## 1. Critical: migration drops widening arithmetic settings

`examples/corev_demo.py` adds `cfg/llvm22.yml` only for an LLVM 22 reference.
There is no corresponding LLVM 23 integration configuration. Consequently,
`behav_to_llvmir` and `behav_to_pat` revert to `no_extend: true`; their validated
LLVM 22 settings use `false`. This can truncate narrow multiplication before
extending the result, making extracted instruction behavior incorrect.

Re-generated all 18 MAC descriptions with the available LLVM 23 PatternGen,
using the same transformed CDSL input and changing only the typing mode:

| Generation mode | MAC checks | Failures with LLVM 23 opt | Failures with LLVM 22 opt control |
|---|---:|---:|---:|
| Default / `--no-extend` | 3,216 | 1,420 | 1,420 |
| Explicit CoreDSL typing | 3,216 | 0 | 0 |

Example: unsigned low-halfword multiplication `0x8000 * 0xffff`, shift zero,
returns `32768` with the default mode instead of `2147450880` (`0x7fff8000`).
This demonstrates a migration configuration bug, not a newly identified LLVM
23 optimizer bug. It is not evidence of an executed LLVM 23 target miscompile:
the check evaluates extracted IR, before target selection.

**Proposed fix:** put version-independent CORE-V generation settings in a
shared configuration loaded for both versions. In particular, preserve
`no_extend: false` in both generation passes. Add a configuration regression
check for both LLVM references and retain the independent MAC semantic checks.

## 2. High: missing LLVM 23 dependency and backend integration

Without the LLVM 22 configuration, automatic dependency selection chooses
`llvm-23.1.3`, whereas the example needs `llvm-23.1.3-packed-simd`.
The normal branch lacks the packed operation feature definitions referenced
by the SIMD model configuration. The version-gated configuration also supplies
memory/branch normalization, capability features and selection patches.
Changing only `LLVM_REF` therefore does not reproduce the validated setup.

**Proposed fix:** add an LLVM 23 overlay selecting the packed-SIMD dependency,
load the shared CORE-V settings, and explicitly carry over the ALU, rotate,
comparison, memory and branch capabilities. Pin the tested dependency revision
when qualifying the resulting build.

## 3. High: three backend patches cannot be applied directly

In a separate scratch source tree, checked the LLVM 22 patch sequence against
the LLVM 23 packed-SIMD dependency. Nine patches apply, packed arithmetic
capabilities are already present, and three fail:

- `corev_rotate_capability`: feature declarations and rotate/funnel-shift
  legalization context differ.
- `corev_minmax_capability`: feature declaration context fails; this also
  depends on the preceding rotate patch having succeeded.
- `corev_packed_compare_capability`: feature declarations, DAG selector and
  target transform cost-model contexts differ.

**Proposed fix:** rebase these patches on LLVM 23, preserving feature gating,
RV32 restrictions, nonmatching funnel-shift fallback, comparison semantics and
baseline behavior. Recheck min/max after porting rotate. The remaining patches
still require compilation and functional testing; successful patch application
alone does not establish API or behavior compatibility.

## 4. Medium: four SIMD C tests silently disappear

The same LLVM 22 conditional adds `tests/simd/*.c`. Evaluating the demo's input
list discovers four such tests for LLVM 22 and zero for LLVM 23.

**Proposed fix:** load the SIMD C tests for both supported versions and assert
the same source-test inventory. Preserve the LLVM 23 internal lit shell already
provided by `seal5/resources/lit.cfg.py`.

## Qualification after the fixes

Build the full LLVM 23 CORE-V backend in isolation. Compare extraction coverage
with LLVM 22 (183 successful descriptions), run the 653 source tests and the
138 generated selection tests, and distinguish the 14 known LLVM 22 exact-opcode
failures from new failures. Repeat arithmetic, clip, rotate and comparison
semantic checks. Finally run the same 21-program Embench comparison through the
validated ETISS model, reporting verification failures and instruction-count
changes against LLVM 22. Keep `cubic`'s existing LLVM 22 legalization failure
separate from new regressions.

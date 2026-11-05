Packed SIMD: TableGen-first investigation
========================================

The initial scope is RV32 packed operations on ``<4 x i8>`` and ``<2 x i16>``
using ordinary TableGen ``Pat`` records. Both GlobalISel's TableGen importer and
SelectionDAG are relevant consumers; direct ``--gisel-table`` matchers are not
part of this investigation. LLVM 22 and 23 remain the target versions.

The feature is named ``GPR32V`` (command-line spelling ``+gpr32v``), rather than
``GRP32V``. It represents packed values in integer registers, independently of
RISC-V V-extension registers. The presence of the feature alone does not prove
that the legalization, extraction and selection paths are connected.

Baseline measured on 2026-11-04
-------------------------------

Four fixtures cover add/subtract on four byte lanes and two halfword lanes.
Each is exercised with ``+gpr32v`` and ``-gpr32v`` on the existing LLVM 22.1.8 and
23.1.3 experimental builds. No toolchain was rebuilt for these probes.

.. list-table:: Outcomes per LLVM version (eight probes per row)
   :header-rows: 1
   :widths: 35 20 45

   * - Probe
     - LLVM 22 / LLVM 23
     - Interpretation
   * - Ordinary TableGen extraction
     - 0/8 / 0/8
     - All four lane-wise instruction descriptions fail extraction, in either
       feature state; no vector-typed packed pattern is produced.
   * - GlobalISel legalization
     - 0/8 / 0/8
     - Explicit scalar/vector bitcasts cannot be legalized, even with the feature.
   * - SelectionDAG compilation
     - 8/8 / 8/8
     - Scalar fallback compiles. These are not packed-instruction selection tests.

There are 48 probes in total. For example, ``PACK_ADD_2X16`` fails ordinary
extraction with ``multiple stores``. Its explicit LLVM IR fails GlobalISel with
``unable to legalize instruction: ... (s32) = G_BITCAST ... (<2 x s16>)``.
The same results occur for four-byte operations. Pattern extraction uses the
default O3 optimization pipeline; explicit-IR probes use O2.

The reproducible driver is ``examples/packed_simd/probe.py``. It saves stdout,
stderr and ``results.json`` in a requested output directory. The initial run is
at ``/tmp/seal5-packed-simd-probes``; its result records are also preserved in
``examples/packed_simd/baseline-llvm22-23.json``. A scalar compilation or process exit code
alone must not be counted as successful packed-pattern support.

Historical sources inspected
-----------------------------

All five linked branches were inspected. The GitHub histories were read through
the GitHub connector. The LRZ branches were reachable with existing SSH access
and fetched into ``/tmp/seal5-packed-simd-research``; source snapshots used for
comparison are under ``/tmp/seal5-packed-simd-baseline/history``. Branch heads
below identify the inspected revisions, not a claim that their tests pass today.

``corev-llvm-project:seal5_paper``
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Head: ``7b1c3965fc2337fc7d63f05ef835768a16fd2c29``.

This is the older SelectionDAG-oriented path. In particular, commit
``632a3a46919e7cef416581e58921103021eb5f3b`` adds packed register classes,
``addRegisterClass`` support for ``v4i8``/``v2i16``, decoder helpers and vector
lowering changes. Later history includes vector insert, abs/min/max and loop
vectorization/interleave tuning. It is a useful reference for register and DAG
integration, not a substitute for current GlobalISel legalization. The branch
also contains disabled CORE-V patterns, so its head should not be treated as an
unqualified working baseline.

Sources: `branch history <https://github.com/PhilippvK/corev-llvm-project/commits/seal5_paper/>`_,
`SIMD backport commit <https://github.com/PhilippvK/corev-llvm-project/commit/632a3a46919e7cef416581e58921103021eb5f3b>`_.

``CoreDSL2LLVM:llvm20_simd``
~~~~~~~~~~~~~~~~~~~~~~~~~~

Head: ``bcbeaf4fd3e3bffd332a556e2ffa7e5e70490c84``.

This is the most direct source of the newer basic GlobalISel work. It includes
feature-gated vector add/sub legalization, scalar/vector bitcasts, vector
load/store handling, element operations, shifts, multiplication, min/max,
reduction handling, target lowering registration and vectorization heuristics.
Relevant commits include:

* ``5c7100257941``: GPR32V legalizer settings.
* ``fa002e143d92``: ``addRegisterClass`` statements for packed types.
* ``52e69af252bf`` and ``d5e04c2fae2a``: multiply and min/max legalization.
* ``122c796c6fd8`` and ``4054446cffc2``: vector reduction work.

Its generated ``ExampleGPR32V.td`` contains the desired shapes, such as
``(v4i8 (add GPR32V4:$rs2, GPR32V4:$rs1))``. However, the branch history explicitly
labels the initial example tests broken; the register definitions use
``PulpV2/PulpV4`` while extraction prints ``GPR32V2/GPR32V4``. The saved example
patterns also use an ALU extension predicate. Generated snapshots are useful
examples, not verified golden outputs. Some operations are gated by
``hasVendorXCVsimd`` and others by ``hasGPR32V``; the port needs a deliberate,
consistent policy rather than wholesale cherry-picking.

Source: `branch history <https://github.com/PhilippvK/CoreDSL2LLVM/commits/llvm20_simd/>`_.

``pattern-gen-loop-iters-fix``
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Head: ``e6536615d15058264380a9dadcd3d73bd6e73071``.

This predates the GlobalISel extractor in the inspected tree. Its history
contains build-vector ordering and vector-extract index fixes, vectorization
heuristics and an experimental iterator-pointer optimization pass
(``7d73c0c9608d``), implemented as a ``MachineFunctionPass`` over machine loops.
The head adds a missing SIMD-extension predicate to patterns;
this is relevant evidence for testing feature gating explicitly. The iterator
pass belongs to a separate loop-optimization investigation; it should not be
assumed necessary merely to select a straight-line packed add.

Source: `branch history <https://gitlab.lrz.de/de-tum-ei-eda-esl/llvm/core-v-llvm-project/-/commits/pattern-gen-loop-iters-fix?ref_type=heads>`_.

``simd-signed-unpacking-tests-rebased``
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Head: ``f94247caf6e33cae848b8480fb2d93e2be184123``.

This extends the GlobalISel experimentation to signed unpacking, notably the
``v2s8`` to ``v2s16`` path and the bridge between ``v2s8`` and scalar ``s16``.
Commit ``8fdbaa5c1b6a`` modifies the legalizer helper, target legalizer and pattern
extractor; the head adds the short-vector bitcasts. The source also contains
broad experimental legalization and commented alternatives. Signed unpacking
needs its own lane-order, sign-extension and narrowing tests after the basic
arithmetic path is established; these settings should not all become generally
legal by default.

Source: `branch history <https://gitlab.lrz.de/de-tum-ei-eda-esl/llvm/core-v-llvm-project/-/commits/simd-signed-unpacking-tests-rebased?ref_type=heads>`_.

``simd-comp-gisel-rebase``
~~~~~~~~~~~~~~~~~~~~~~~~

Head: ``448f4dad71e5cf7abbf0e6fe998a0db16adc99a2``.

This is the comparison/scalar-replication experiment. Commit ``47eff9aaef76``
adds extensive vector-compare and replication legalizer settings. Its extractor
and register definitions both use the older ``PulpV`` names. It is a reference
for comparison-result widths and replicated scalar inputs, not proof that the
current generic compare legalization is ready. The head reverts generated test
and SIMD patterns, another reason not to treat the branch head as a passing
selection baseline.

Source: `branch history <https://gitlab.lrz.de/de-tum-ei-eda-esl/llvm/core-v-llvm-project/-/commits/simd-comp-gisel-rebase?ref_type=heads>`_.

Current integration gaps
------------------------

1. **Feature predicate.** The inspected CoreDSL2LLVM LLVM 23 source defines
   ``HasGPR32V`` with the predicate string ``Subtarget->hasGPR32V)``; it should
   call ``hasGPR32V()``. Because the baseline never reaches a vector matcher,
   simply seeing that the current toolchain builds does not validate this unused
   predicate's generated C++.
2. **Register classes.** The ordinary extractor emits ``GPR32V2/GPR32V4``, while
   target definitions retain ``PulpV2/PulpV4``. Names, target-lowering registration,
   decoder support and register-bank handling must agree. RV64 additionally
   needs a separate mapping: the current vector operand printer asserts RV32.
3. **Legalization.** The modern target legalizer lacks the historical GPR32V
   path. First restore only the required scalar/packed-vector bridges and basic
   arithmetic, with precise types and feature predicates. Do not import broad
   ``alwaysLegal`` rules from experiments.
4. **Vectorization before extraction.** The lane-wise descriptions currently
   remain multiple stores. PatternGen already enables SLP vectorization; the
   missing lowering/type-cost configuration must be addressed and the resulting
   single packed output verified. This is one packed destination, not a reason
   to enable the unrelated multi-output matcher.
5. **Seal5 import/configuration.** ``examples/common/cfg/simd_patches.yml`` still
   contains ``?`` placeholders. The common RISC-V configuration requests
   ``gpr32v``, but its sample vector legalization entries are commented out.
   The current backend importer covers the scalar/memory/branch and direct
   matcher support; it does not import the full SIMD feature, register-class,
   target-lowering and target-cost changes. These must become explicit,
   version-matched support for a clean upstream LLVM checkout.
6. **Pattern predicates.** ``riscv_instr_info/writer.py`` still has a TODO for
   requiring ``HasGPR32V`` with packed classes. Generated packed rules should
   require both the applicable instruction-set feature and the packed-register
   capability. Enabling a representation feature alone must not imply arbitrary
   packed instructions exist.

Proposed implementation gates
-----------------------------

* Start with RV32 add/subtract on ``v4i8`` and ``v2i16``. Resolve the naming and
  feature predicate, restore the minimum register/lowering and legalization
  support, and verify that SLP produces a single vector output. Keep all output
  as ordinary TableGen ``Pat`` records.
* Build the generated TableGen definitions and check GlobalISel import. Run one
  codegen file per instruction, with both feature states, object decoding and
  packed-lane overflow/isolation checks. Compare generated patterns with a small
  hand-written reference so extraction and selection failures are separable.
* Verify the SelectionDAG consumer separately. Its scalar fallback successes
  above are not adequate packed-selection evidence.
* Then add constant shifts, multiplication and signed/unsigned min/max. Only
  after those pass, examine replicated scalar/immediate operands, comparison
  masks, signed unpacking, reductions and dot products. Iterator/vectorizer
  heuristics are a later performance task.

Working LLVM 22/23 port
-----------------------

The first gate above now works on both versions: packed add/subtract for RV32
``v4i8`` and ``v2i16``. The local CoreDSL2LLVM branches are
``llvm-22.1.8-packed-simd`` and ``llvm-23.1.3-packed-simd``. These branches build
on the existing PatternGen work and adapt the LLVM20 register/lowering approach
to each version's APIs. They have not been pushed.

The port fixes the GPR32V predicate and register-class names, registers the packed
DAG types, restores precise GlobalISel legalization/register-bank rules, and adds
scalar/vector register-class bridges. Packed memory transfers use scalar words;
unaligned addresses retain normal target lowering. Natural alignment on synthetic
register-storage arguments lets SLP combine lane writes into one packed output.
This alignment does not apply to memory addresses represented by those registers.

Seal5 imports this version-matched support and requires ``HasGPR32V`` in generated
packed patterns, preserving ISA and XLEN predicates. The demo ISA additionally
requires ``HasStdExtXPackedSIMD32``. Autogenerated MIR tests allow a register-class
copy between a packed instruction and its scalar result writeback.

Validation on each version:

* Four extracted vector patterns; no direct matcher output.
* Eight passing integrated demo test files: four handwritten and four generated.
* Both selectors at O0/O2/O3, with GlobalISel fallback prohibited.
* Correct optimized subtraction operand order, aligned and unaligned vector
  memory transfers, object decoding, and disabled-feature checks.
* Backend import patches apply cleanly to the matching upstream LLVM sources.
* Seal5: 62 unit tests pass. Native RISC-V GlobalISel: 450/450 on LLVM 22
  and 469/469 on LLVM 23. The LLVM 23 object-symbol test uses the existing
  matching-version llvm-readobj utility from the normal demo build.

Run ``examples/packed_simd_demo.py`` using the matching local branch; commands
and the standalone verifier are documented in ``examples/packed_simd/README.md``.
The baseline and gaps above describe the pre-port investigation. RV64 and the
remaining SIMD operations are still unverified and are not enabled by this demo.

Initial real-source vectorization: Embench
-----------------------------------------

The compile-only Embench experiment in
``examples/packed_simd/results/embench-llvm22-23.md`` tests 22 programs / 26 C
translation units with default O3 vectorization. It compares disabled
vectorizers, the native target, and the packed target on both LLVM versions.

It exposed and fixed two RVV-only cost-query paths reached by GPR32V vectors.
All translation units now optimize successfully. Packed codegen succeeds for
19/26 units with SelectionDAG and 18/26 with GlobalISel, but none of those objects
contains a demo packed instruction. The optimizer does form packed arithmetic
in other units, whose surrounding vector operations prevent code generation.
The synthetic add/sub selection result therefore does not yet extend to
successful complete vectorized Embench programs. No runtime speedup was measured.

The report records the first blockers and a source hash manifest; the runner
``examples/packed_simd/embench.py`` retains IR, optimization remarks, commands,
object disassembly and diagnostics for subsequent work.

Implemented real-source flow
----------------------------

The follow-up report ``examples/packed_simd/results/implemented-llvm22-23.md``
records working benchmark execution after adding packed construction, loop PHIs
and scalar fallback for unsupported operations. DSP widening, multiplication,
shifts and narrowing can now surround packed halfword addition. Shuffles,
comparisons/selects and narrow memory transfers also have fallback paths.

Packed add/sub capability flags are distinct from the GPR32V representation;
``ExtensionsSettings.backend_features`` lets a generated ISA imply precisely
those backend capabilities. Shuffle, packing and unaligned-memory costs now
reflect instruction expansion instead of the shuffle placeholder.

All 26 Embench translation units compile with SelectionDAG, and 25 with
GlobalISel, on LLVM 22 and 23. Complete executables pass benchmark verification
for 22/22 programs and 21/22 respectively. The remaining GlobalISel failure is
the scalar-control ``cubic`` long-double comparison case.

Default O3 selects packed instructions in ``edn`` and ``md5sum`` when efficient
unaligned scalar memory is enabled for both packed and native controls. Retired
instruction reductions are 1.55--2.24 percent and 7.57--7.67 percent, with code-size
growth. Strict-alignment costing does not select these packed instructions in
this snapshot. Measurements use Spike's CPI=1 model and do not establish hardware
cycle speedups. The report includes reproducible compile/execute/replay commands,
source hashes, all-program comparisons and correctness checks.

Pattern extraction, direct GISel-table entry counts, generation times and output
sizes can be collected with the :doc:`pattern-metrics` reports.

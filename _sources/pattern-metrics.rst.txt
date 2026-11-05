Pattern generation metrics
==========================

Seal5 records measurements for each PatternGen invocation in
``<instruction>.td.stats``. The existing LLVM statistics groups are preserved;
additional measurements live under ``seal5``. This works without LLVM statistics
support, including for failed invocations and format-only generation.

The PatternGen writer automatically emits ``pattern_gen_manifest.json``,
``pattern_gen_report.json`` and ``pattern_gen_report.csv`` in each model's
temporary output directory. The manifest records current-run instructions,
including skipped and failed instructions. The reports contain instruction,
set and model-global rows. Numeric totals also enter the existing pass metrics.

For a report across all models in an existing workspace::

   python -m seal5.backends.report.pattern_gen.writer \
     --yaml /path/to/.seal5/settings.yml \
     --scope all --output pattern-metrics.json

Use ``--scope instruction``, ``set`` or ``global`` to restrict the report.
``--agg`` is an alias for ``--scope global``. CSV, Markdown and pickle output
remain supported. Aggregated output now contains one row per aggregation scope,
rather than the old two-column raw LLVM statistic sums.

Metric definitions
------------------

* ``n_sets`` counts distinct (model, set) identities, including sets containing
  only skipped instructions. ``n_processed_sets`` counts sets with at least one
  attempted invocation. Parsed-set counters from separate subprocesses are not
  added to estimate the number of sets.
* ``n_instructions`` counts instructions considered by the writer;
  ``n_processed_instructions`` excludes skipped instructions. ``n_success``,
  ``n_failed`` and ``n_skipped`` describe instruction outcomes, not pattern counts.
* ``n_extracted_patterns`` is the number of generated rules/entries, using the
  PatternGen counter when present, otherwise its ``Pattern for`` output records.
  One instruction can produce multiple patterns. Extraction does not establish
  importability, test coverage or semantic correctness.
* ``n_tablegen_patterns`` counts ordinary TableGen patterns;
  ``n_gisel_table_patterns`` counts extracted roots for direct GISel generation.
  ``n_gisel_table_entries`` counts the expanded RuleMatcher entries, including
  permutations of commutative operands. For example, the scalar NAND example
  extracts one pattern but emits four entries. Entry counting recognizes the
  current emitter's literal permutation-loop syntax; unfamiliar control flow
  yields an unavailable count. Direct entries bypass the
  SelectionDAG-to-GlobalISel importer.
* ``pattern_gen_time_s`` sums subprocess elapsed times, measured with a monotonic
  clock. ``tablegen_time_s`` and ``gisel_table_time_s`` separate the two generation
  modes. They include parsing, optimization, extraction and output in that
  invocation, including format generation when requested. They exclude LLVM
  builds and Seal5 postprocessing. They are not internal phase timings.
* ``generation_wall_time_s`` in the writer's global report/pass metrics measures
  the generation phase including Seal5 postprocessing, excluding model loading
  and report serialization. Parallel subprocess time sums can exceed this
  wall time; do not interpret them as CPU time.
* ``tablegen_bytes`` counts UTF-8 file bytes in the final per-instruction ``.td``
  output plus its instruction-format ``.td`` when requested. This includes final
  feature predicates and pattern-priority adjustments, but excludes shared
  include scaffolding. Direct GISel mode can also generate TableGen definitions;
  these bytes are kept separate from its matcher table.
* ``gisel_table_bytes`` counts the final generated ``.inc`` files.
  ``gisel_table_patch_bytes`` counts corresponding ``.inc.patch`` sidecars:
  reproducible unified addition patches targeting
  ``llvm/utils/TableGen/seal5/<set>/<instruction>.inc``. These include diff headers
  and line prefixes. They measure matcher-table payload patches, not the entire
  backend support patch or shared GlobalISelEmitter include changes. Seal5 still
  installs the table through its existing File artifact; the sidecar is for
  measurement/reproduction, not an additional patch to apply in the flow.

Sizes count generated artifacts even if an invocation subsequently fails;
absent files have size zero. Skipped instructions contribute zero. Failed
subprocesses retain their timing and return code. A new invocation removes old
output artifacts before measuring. Current-run manifests prevent stale statistics
from skipped instructions from re-entering the report.

Import and match evidence
-------------------------

The reports distinguish ``n_tablegen_patterns_imported``,
``n_tablegen_patterns_matched`` and ``n_gisel_table_patterns_matched`` and ``n_gisel_table_entries_matched``. Importing
means acceptance by the GlobalISel importer, not selection at runtime. Matching
means a distinct generated rule/entry was selected in codegen validation, not
that the generated instruction has been proved semantically correct. Multiple
executions of one rule count once. Direct entries have no importer count.

Current PatternGen versions do not provide per-pattern import or match evidence.
Their counts are therefore unavailable (JSON null / empty CSV cells), not zero
and not the extraction count. Whole-backend ``gisel-emitter`` totals are retained
in raw statistics but cannot be attributed to one generated instruction.
If an instrumented PatternGen emits scoped ``Imported patterns`` / ``Matched
patterns`` counters in its ``pattern-gen`` group, these are consumed directly.

Alternatively supply ``--validation evidence.json``. This is a JSON list, with
one entry per (model, set, instruction, mode)::

   [
     {
       "model": "Example", "set": "XExample", "instruction": "ADD3",
       "mode": "tablegen",
       "imported": [0, 1], "imported_source": "artifacts/import-records.json",
       "matched": [1], "matched_source": "artifacts/rule-coverage.json"
     }
   ]

Indices are zero-based in the generator's pattern-output order. A supplied list
is a complete result for that invocation: an empty list means zero validated
patterns, whereas an omitted list means unavailable. The source field identifies
the evidence to retain with the experiment; the reporter validates identities,
index ranges and duplicates, but does not independently verify that evidence.
Use ``mode: gisel_table`` for direct generation: ``matched`` identifies extracted
roots, while ``matched_entries`` / ``matched_entries_source`` can independently
record expanded-entry coverage, with indices in emitted entry order. Do not
supply ``imported`` for direct generation. A passing
instruction-level FileCheck test cannot establish which of several alternative
patterns matched: supply rule-level evidence rather than counting every pattern
of the instruction as tested.

An aggregate remains unavailable if any contributing instruction lacks that
measurement. ``*_known`` reports the measured subtotal and
``*_unreported_instructions`` reports the missing population. This prevents a
partial coverage result from appearing to be a complete total.

Reports also accept older ``.td.stats`` files without a manifest. In this case
instruction enumeration, timing, sizes and generation mode may be incomplete;
regenerate the artifacts for a controlled experiment. Older files are assumed
to use ordinary TableGen mode because they did not record the generation mode.

# Seal5 dissertation figures

These figures document the current checkout's implementation, rather than an
idealized pipeline. Use the vector PDFs in LaTeX; SVGs are editable in Inkscape
and PNGs are previews. Text remains selectable in the PDFs.

| Figure | Vector PDF | Editable source | Preview |
|---|---|---|---|
| Sequential stages, grouped by lifecycle role | [01-stages.pdf](01-stages.pdf) | [SVG](01-stages.svg) | [PNG](01-stages.png) |
| All registered passes, order and scope | [02-passes.pdf](02-passes.pdf) | [SVG](02-passes.svg) | [PNG](02-passes.png) |
| Full fresh-run flow, including repeated builds | [03-full-flow.pdf](03-full-flow.pdf) | [SVG](03-full-flow.svg) | [PNG](03-full-flow.png) |

The pass inventory is dense: use a landscape page or a large-format appendix.
The overview and full-flow figure can be scaled independently. Colors supplement
explicit labels, so model/global scopes and phase numbers remain distinguishable
in grayscale.

## Proposed captions

1. **Sequential Seal5 stages for a fresh run with PatternGen.** Numbered boxes
   proceed left to right within each row, then to the next lifecycle group:
   preparation, construction, validation, and delivery. Repeated patch, build,
   and generation calls are shown in their execution positions. The intermediate
   construction build groups the instruction-aware build and the extraction-tool
   targets. Dashed boxes identify optional reset and delivery operations.
2. **Registered Seal5 pass pipelines and execution scopes.** The transformation
   pipeline comprises 38 entries, followed by 12 top-level generation entries.
   The final generation entry expands into four PatternGen passes. M denotes
   per-model execution and G denotes global execution. Asterisks mark explicitly
   conditional passes; configuration filters may skip other passes as well.
3. **Seal5 compiler-generation flow for a fresh run with integrated PatternGen.**
   Bootstrap support is applied before the first build; structural artifacts
   precede the instruction-aware build; selection patterns precede the final
   build. The inset distinguishes PatternGen pass order from artifact
   dependencies. Validation and optional delivery follow compilation.

## Separate patch-phase table

[01-patch-phases.tex](01-patch-phases.tex) contains an input-ready TeX table;
[01-patch-phases.pdf](01-patch-phases.pdf) is its compiled preview. The table
replaces the patch-phase panel that was previously part of `01-stages`.
It describes phases 0–5, including the unassigned custom-patch slots, separately
from the lifecycle flow.

Include it with `\input{figures/01-patch-phases.tex}` after loading `booktabs`
and `tabularx`. The optional `01-patch-phases-preview.tex` wrapper is only for
preview compilation, not for inclusion in the dissertation.

## Accuracy and scope

- Registered order comes from `TRANSFORM_PASS_MAP` and `GENERATE_PASS_MAP` in
  `seal5/flow.py`. Nested order comes from `pattern_gen_pass` in
  `seal5/pass_list.py`. Commented-out entries are not executed.
- Scopes follow `Seal5Flow.create_passes`: all transforms are MODEL; only
  `riscv_gnu`, `seal5_td`, `riscv_field_types` and `riscv_gisel_legalizer` are
  GLOBAL generators. All nested PatternGen passes are MODEL. File splitting by
  instruction does not imply INSTR scope.
- The pass manager traverses each registered list sequentially. Instances of one
  MODEL pass can run concurrently across input models. `Seal5Pass.order` is
  marked unsupported and does not sort the pipeline.
- SET is marked unsupported in the API (a dispatcher branch exists); none of
  these registered passes uses it. INSTR has no execution implementation.
- `gen_model_td` is an available handler in `seal5/pass_list.py`, but is not
  registered. It expects an input model and emits phase-1 artifacts; it therefore
  has no position in the default sequence. Repeated names such as `infer_types1`
  and `infer_types2` are distinct registered invocations of a shared handler.
- The four explicit normalization/branch passes are registered but default to
  `enabled=False`. GNU integration requires a source tree. The figure does not
  imply that every registered pass necessarily changes every instruction.
- The full-flow figure follows `run_seal5_flow` in `seal5/wrapper.py`, with the
  default integrated PatternGen mode and a fresh build. It labels reuse,
  PatternGen skipping and test-only behavior. Individual lifecycle flags can
  alter a particular run. Setup can alternatively build a separate extraction
  toolchain when integrated mode is disabled.
- The wrapper calls `generate(skip=["pattern_gen"])` before phases 1–2 and
  `generate(only=["pattern_gen"])` later. Ordering generation passes does not
  imply the same ordering of patch application: the latter follows patch phase
  and priority. The optional GNU patch is emitted separately and is not assigned
  an LLVM patch phase.
- In the nested pipeline, `llvmir_to_gmir` consumes the LLVM IR artifact.
  `behav_to_pat`, however, invokes PatternGen on reduced CoreDSL again; it does
  not consume the previous `.gmir` file. Its internal extraction builds its own
  IR/GMIR representation. The figures deliberately preserve this distinction.
- Lifecycle `export` archives metadata/artifacts; report scripts are separate
  consumers of those results. The figures do not claim that a report script is
  a registered pass or a mandatory wrapper stage.

`passes.csv` records each registered invocation, handler, scope, options, source
line and emitted LLVM patch phase. `sources.json` contains SHA-256 fingerprints
of the five implementation files used for this snapshot. These fingerprints
also capture local source edits that a Git revision alone might miss.

## Regenerate

From the repository root:

```sh
python3 docs/figures/seal5/generate.py                # SVG, TeX table + catalogs
python3 docs/figures/seal5/generate.py --render       # figure PDFs + PNGs; Inkscape
python3 docs/figures/seal5/generate.py --render-table # table PDF; pdflatex
```

Both Inkscape 0.92 and current command-line syntax are supported. The generator
reads Python ASTs without importing Seal5 or launching compiler builds. It
checks the current scope list and pass counts so a changed registration cannot
silently produce an incomplete diagram. Geometry, labels and palette are in
`generate.py`; individual SVGs can also be edited directly.

## LaTeX

With `graphicx`, `booktabs`, `tabularx` and, for the pass inventory, `pdflscape`:

```latex
\begin{figure}[tbp]
  \centering
  \includegraphics[width=\linewidth]{figures/01-stages.pdf}
  \caption{Sequential Seal5 stages, grouped by lifecycle role.}
  \label{fig:seal5-stages}
\end{figure}

\input{figures/01-patch-phases.tex}

\begin{landscape}
\begin{figure}[p]
  \centering
  \includegraphics[width=\linewidth,height=.88\textheight,keepaspectratio]
    {figures/02-passes.pdf}
  \caption{Registered Seal5 passes in execution order, with their scopes.}
  \label{fig:seal5-passes}
\end{figure}
\end{landscape}

\begin{figure}[p]
  \centering
  \includegraphics[width=\linewidth,height=.9\textheight,keepaspectratio]
    {figures/03-full-flow.pdf}
  \caption{Seal5 compiler-generation flow with integrated PatternGen.}
  \label{fig:seal5-full-flow}
\end{figure}
```

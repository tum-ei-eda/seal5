# CORE-V validation results

## LLVM 23 migration

The [LLVM 23 validation](llvm23-validation.md) records the completed port:
651 source tests pass, generated selection/extraction coverage matches LLVM 22,
and all 21 supported Embench programs verify in both variants. The one-repeat
[LLVM 23 run](embench-llvm23-main.md) and [cross-version instruction table](llvm22-23-instructions.md)
record performance changes, including the remaining PicoJPEG and SGLIB regressions.

## LLVM 22 reference

The current [full table](embench-llvm22-main.md) and
[machine-readable results](embench-llvm22-main.json) use upstream CDSL main
`56b66cfea193b28cd88ea89a684469ef76fa31cc`, regenerated LLVM 22 and ETISS.
See [validation coverage and remaining gaps](main-validation.md) and
[exact model hashes](main-model-manifest.json).

- 21 programs verify in both variants, three repetitions each: **126 verified
  executions**, with identical repeated instruction counts.
- Geometric mean baseline / CORE-V instruction ratio: **1.0585**, equivalent
  to **5.52% fewer executed instructions**.
- All verified instruction counts match the previous reviewed-model run.
- `cubic` fails compilation in both variants because GlobalISel cannot legalize
  an s128 floating-point comparison; it is excluded from the ratio.
- Source codegen: **651 passed**, 2 unsupported, zero failures. Native ETISS:
  **4,592 checks**, zero failures. Generated selection tests retain 14 exact
  opcode failures, detailed in the validation report.

This measures executed instructions. ETISS model cycles assume CPI=1 and do
not establish hardware speedup or an official Embench score. Initialization,
warmup and verification are excluded; marker/call overhead is included.
Raw commands, IR, disassembly and run output remain in
`/tmp/seal5-corev-embench-main`. The JSON records compiler, runtime and source
hashes; its absolute artifact paths refer to that retained directory.
Use `../benchmark_embench.py --help` to reproduce with local tool/model paths.

## Historical reviewed-model run

# Reviewed-model Embench results

The [full table](embench-llvm22-reviewed.md) and
[machine-readable results](embench-llvm22-reviewed.json) record the completed
LLVM 22 comparison using the [reviewed CDSL integration](../review/README.md).

- 21 programs verify in both variants, three repetitions each: 126 verified
  executions. All repeated instruction counts are identical.
- `cubic` fails compilation in both variants: GlobalISel cannot legalize an
  s128 floating-point comparison in SolveCubic. It is excluded from ratios.
- Geometric mean baseline / CORE-V instruction ratio: **1.0585**, equivalent
  to **5.52% fewer executed instructions** across the 21 verified pairs.
- Largest reductions: SHA-256 22.75%, EDN 22.18%, integer matrix multiply
  16.46%, AES 15.51%. SLRE executes 8.38% more instructions with CORE-V.

This measures executed instructions, not hardware timing or an official Embench
score. Model cycles are CPI=1 here. Initialization, warmup and verification are
outside the measurement region; marker/call overhead is included.

All 42 executable SHA-256 hashes match the earlier, faulty-simulator run, and
all 21 baseline instruction counts are unchanged. The compiler was held
constant. AHA, AES, SHA-256, primecount and QRduino now verify; they failed on
the old simulator. The raw command/IR/disassembly/run artifacts remain in
`/tmp/seal5-corev-embench-reviewed`, with the previous run preserved in
`/tmp/seal5-corev-embench-o3`. The JSON contains absolute artifact paths from
this machine; those paths require the retained run directories.

[Instruction-check output](instruction-checks.txt) records 4,592 independent
raw-encoding regression checks with zero failures on the regenerated model.
The tests are in `../benchmark_runtime/instruction_checks.c`.

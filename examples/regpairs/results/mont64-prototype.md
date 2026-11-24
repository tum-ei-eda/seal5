# aha-mont64 funnel and unsigned comparison prototypes

LLVM 23, RV32IM plus existing register-pair support and word-cost lowering fix.
Only two expressions in `modul64` are replaced in an external source copy:
`(x << 1) | (y >> 63)` and `(x | t) >= z`. The benchmark's algorithm and
verification remain intact. These are explicit inline assembly experiments,
not automatic pattern extraction or compiler instruction selection.

| Variant | O2 retired instructions | O3 retired instructions |
|---|---:|---:|
| Control, including earlier lowering fix | 4,117,602 | 4,101,951 |
| Funnel shift only | 3,305,442 | 3,289,791 |
| Unsigned comparison only | 4,114,217 | 4,098,566 |
| Both | **3,302,057** | **3,286,406** |

The one-bit funnel saves 812,160 instructions, **19.8%** of the O3 control.
The comparison saves just 3,385 (**0.08%**). Combined, the reduction is 19.9%
beyond the lowering fix, or 40.8% relative to the earlier RV32IM count of
5,551,141. These are retired instruction counts, not measured hardware speedups.
All eight runs pass Embench verification and 1,024 additional randomized
semantic cases for both prototypes, including equality and zero comparisons.
Semantic checks run during initialization outside the measured region.

The funnel prototype has two pair sources and one pair destination, computing
`(a << 1) | (b >> 63)`. Its count is fixed at one; this experiment does not
establish results for a general immediate/variable funnel-shift instruction.
The comparison has two pair sources and one scalar Boolean destination.
The separate Spike functional model uses custom-2 opcode `0x5b`, avoiding the
custom-0 pair and custom-1 marker/packed instruction encodings.

An initial experiment forced a0/a1 and a2/a3. Its register moves distorted the
result: O3 funnel 3,613,808, comparison 4,423,852, both 4,910,724. The final
experiment instead uses LLVM's existing `R` pair operand constraint and `r`
scalar result constraint, allowing register allocation to choose legal pairs.
Those exploratory results are retained in the raw JSON. Even the final result
includes inline-assembly boundaries and pair construction/extraction costs;
automatic lowering and branch folding could change the comparison outcome.

Recommendation: integrate the funnel first. A general funnel would need count
encoding and semantics, assembler/builtins, lowering, and independent tests on
LLVM 22 and 23. Keep unsigned comparison a lower priority until its native
lowering/branch behavior can be assessed. No compiler rebuild was required for
this experiment. The experimental CDSL specification in
`../cdsl/experimental/Mont64.core_desc` is not selected by the configuration
and has not been run through the generator or validator.

Reproduction (reference directory from `benchmark_mont64.py`):

```sh
python examples/regpairs/benchmark_mont64_prototype.py \
  --reference /tmp/seal5-mont64-regpairs-word-costs \
  --output /tmp/new-mont64-prototypes \
  --spike-source /tmp/m2isar-spike --spike-build /tmp/m2isar-spike-build
```

[Raw measurements](mont64-prototype-llvm23.json). Full commands, source copies,
logs and binaries: `/tmp/seal5-mont64-funnel-compare-allocated`.

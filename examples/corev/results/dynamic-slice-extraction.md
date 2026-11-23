# Dynamic slice bounds: parser fix and extraction reassessment

The archived `seal5-diss-exp` attempt
`20261123T162843Z-65e500a2ff4b4cc89526ee83ced9f80a` used Seal5
`a57ab31c913cd2c3b618d869e99ff3f1772a76b3`, PatternGen
`7649b4dd84de9ab18c17fd0989e13edf39fc03c3` and definition-integrated LLVM
`32c961d9b615176ea9a48de4ca0fb16d122763ac`.

## Cause and fix

The exact archived `SEAL5_CV_EXTRACT_H` input reproduces the IntegerType
assertion with the pinned compiler. Its backtrace reaches:

```
__assert_fail
llvm::ConstantInt::get(llvm::Type*, unsigned long, bool, bool)
gen_subscript(...)
ParseExpression(...)
```

The parser computes the upper limit for `base +: 16` before loading the local
`base` variable. Its LLVM value is still an alloca pointer, so requesting an
integer constant with that pointer type triggers the cast assertion. This
representative failure is not a vector type being mistaken for an integer.

`llvm22-dynamic-slice-bounds.patch` loads and normalizes the first bound before
constructing limit expressions. It also fixes the normalization loop to resize
its current bound (`*v`) rather than always resizing `lower`. This small fix
already existed inside the later register-pair parser adapter; it is now
available independently through the shared CORE-V configuration. The config
skips dependencies that already load the upper bound.

## Isolated validation

The original cache was mounted read-only in the pinned Docker image. Only
`Parser.cpp` was compiled, then linked against the unchanged cached object files
and LLVM libraries. Source, object, binary, exact build commands and outputs are
under `/tmp/seal5-simd-parser-fix`, with the separate build directory at
`/tmp/seal5-simd-parser-fix/build`. No original cache or result files were changed.

All 284 archived extraction commands were replayed with only the binary and
input/output locations replaced. The original 26 skipped instructions were not
rerun. No previously successful extraction was lost.

| Model | Successful | Failed | Skipped | Patterns |
|---|---:|---:|---:|---:|
| XCoreVAlu | 31 | 0 | 0 | 379 |
| XCoreVBitmanip | 4 | 1 | 10 | 5 |
| XCoreVBranchImmediate | 2 | 0 | 0 | 2 |
| XCoreVMac | 18 | 0 | 0 | 390 |
| XCoreVMem | 8 | 0 | 16 | 8 |
| XCoreVSimd | 124 | 96 | 0 | 184 |
| **Total** | **187** | **97** | **26** | **968** |

All 15 original assertions disappear. Signed/unsigned byte/halfword EXTRACT
produce four new patterns. Nine shuffle variants reach the existing multiple
stores limitation; INSERT_B/H reach `cannot assign rvalue`. Scalar EXTRACT's
separate s33 legalization failure remains.

The targeted fixture verifies signed/unsigned halfword slices through a local
five-bit bound and a wider 64-bit bound. All 420 edge/random constant-folded
cases agree with an independent integer reference. The Python suite reports
216 passed, 1 optional test skipped, and 310 subtests passed. The patch applies
cleanly to both available LLVM 22 and LLVM 23 dependency sources. Run the
semantic regression with:

```sh
python examples/corev/check_dynamic_slice_bounds.py \
  --pattern-gen /path/to/pattern-gen --opt /path/to/opt \
  --output /tmp/dynamic-slice-regression
```

[Machine-readable assessment](dynamic-slice-extraction.json) records the pinned
identities and per-model changes. The patch is configured for both CORE-V
versions, but this isolated binary reassessment used LLVM 22 only. These are
extraction and IR-semantics results; final pattern integration, a final target
compiler rebuild and target execution were not performed.

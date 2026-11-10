# Direct GlobalISel pattern example

This example opts into PatternGen's experimental `--gisel-table` backend on
LLVM 22 and 23. The default backend for other models remains TableGen `Pat`
records. Direct matching requires the matching CoreDSL2LLVM experimental branch;
stock LLVM does not implement these matcher extensions.

The model contains RV32 and RV64 versions of NAND, three-input addition,
accumulating subtraction, an immediate shift, unsigned maximum, and a two-result
sum/difference instruction. The first five instructions also have ordinary
TableGen patterns. Sum/difference uses direct matchers to combine two arithmetic
instructions sharing their inputs.

`cfg/passes.yml` selects `behav_to_pat.gisel_table` for this model and gives its
patterns priority over native instruction selection. It also explicitly names
`rd1` and `rd2` as destinations for zero-register guard normalization. Inputs are
snapshotted before either destination is written, preserving input/output alias
semantics.

Each instruction has its own codegen test file. Tests require GlobalISel without
fallback, verify selected assembly and object decoding, and check native code
when the extension is disabled. The two-result tests exercise both IR definition
orders. Generated tests additionally check writeback of both results.

Two-result eligibility currently covers pure arithmetic only. Memory operations
with register writeback, mixed load/store operations, and three or more register
outputs remain excluded. The matcher conservatively rejects cross-block merges
and merges that would move a result past an intervening use.

The driver is `examples/gisel_table_demo.py`; select an LLVM version with
`LLVM_REF=llvmorg-22.1.8` or `LLVM_REF=llvmorg-23.1.3`. The version configuration
files specify the corresponding experimental CoreDSL2LLVM branch. To use a local
repository, set `REPO_URL_CoreDSL2LLVM=file:///path/to/CoreDSL2LLVM`.

For local experimental branches, run from the Seal5 checkout:

```sh
source venv310/bin/activate
REPO_URL_CoreDSL2LLVM=file:///work/git/CoreDSL2LLVM \
LLVM_REF=llvmorg-22.1.8 BUILD_CONFIG=release_assertions \
SEAL5_NUM_THREADS=1 TEST=1 INSTALL=0 DEPLOY=0 EXPORT=0 \
DEST=/tmp/seal5_gisel_table22 python3 examples/gisel_table_demo.py
```

Use `LLVM_REF=llvmorg-23.1.3` and a different destination for LLVM 23. The example
branch names must exist in the selected repository; these experimental branches
are currently local and are not assumed to exist on the public remote.

The standalone extraction/selection comparison and conservative multi-output
safety checks are documented in CoreDSL2LLVM's `core_descs/GISelTable.md`.

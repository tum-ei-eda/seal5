# LLVM 23 normalization example

`examples/demo.py` includes this example and its configuration when
`LLVM_REF=llvmorg-23.*`. Only the
`Normalization` model enables the optional memory, register, and subscript
passes. Branch lowering stays disabled for LLVM 23.

The example covers:

- RV32 dynamic scalar slices in both directions, with inclusive widths.
- RV32 little-endian halfword/XLEN loads and halfword stores.
- RV64 XLEN loads and automatic low-word register names.
- Manually written `MEM8`, `MEM32`, and `XW` accesses.
- GlobalISel instruction selection and assembler/disassembler round trips.

Run the full demo using the repository's Python environment:

```sh
export PATH=/nfs/TUEIEDAscratch/ga87puy/work/cpython_v3.10_nodbgopt/install/bin/:$PATH
source venv310/bin/activate
SEAL5_LOG_LEVEL=info SEAL5_NUM_THREADS=1 VERBOSE=0 PREPATCHED=0 PROGRESS=1 \
LLVM_REF=llvmorg-23.1.3 CCACHE=1 CLONE_DEPTH=1 BUILD_CONFIG=release_assertions \
IGNORE_ERROR=1 TEST=1 INSTALL=0 DEPLOY=0 EXPORT=0 BUILD_CACHE=0 \
DEST=/tmp/seal5_llvm_demo_llvm23 python3 examples/demo.py
python3 examples/normalization/check_llvm23.py /tmp/seal5_llvm_demo_llvm23
```

The extra checker also runs automatically after the LLVM 23 demo tests. It
verifies the normalized split CDSL and invokes the built
pattern-gen on the memory instructions. It checks LLVM load/store widths and
writes a JSON report to `.seal5/temp/normalization_checks/results.json`.
Memory selection patterns are currently skipped by Seal5, so MC tests alone
would not verify their behavioral lowering.

The example applies a small LLVM 23 pattern-gen patch for dynamic slices.
The original aligned-access shortcut rounded variable offsets down to element
boundaries. The patch limits that shortcut to proven aligned constants; the
code-generation test includes an unaligned three-bit offset.

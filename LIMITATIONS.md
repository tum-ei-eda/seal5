# Limitations

- RV32I only
  - Extending RISCVBase is not allowed due to undefined XLEN, see Issue #15
  - RV64I support is untested (Flow does currently assumes 32 bits), see Issue #26
  - Non-integer (i.e. float) support is planned, see Issue #20
  - Compressed instruction support is planned, see Issue #21
  - CSR instruction/register support is planned, see Issue #39
- Codegen Limitations (Patterns)
  - GlobalISel only, ISelDAG backwards-compatibility is planned, see Issue #11
  - Single output-only
  - Single basic block (?)
  - No memory access
  - No branches/jumps
- TODO

## Known Bugs

### Clang `-march` parser does not pick up new extensions

Due to issues with the ordering of extensions in `RISCVISAInfo.cpp` the search algorithm will not find entries which not inserted in the correct order. To deal with this issue the following workaround is recommended:

- Only generate patches for a single model (CoreDSL file)
- Make sure that the `arch` string always starts with an `x`, or better prefix every arch string with `xseal5`.

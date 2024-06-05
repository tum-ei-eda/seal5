# Limitations

- Unsupported Instruction Types
  - Memory
  - Branch
  - CSR instructions
- Unsupported DataTypes
  - Float (`f32`,...)
  - Vectors except (`v2i16`, `v4i8`)
  - Scalars except (`i8`, `i16`, `i32`, `i64`)
- Codegen Limitations (Patterns)
  - GlobalISel only, ISelDAG backwards-compatibility is planned, see Issue #11
  - Single output-only
  - Single basic block (?)
  - No memory access
  - No branches/jumps
- SIMD Support
  - Work in Progress (GlobalISel limitations need to be fixed first)

## Known Bugs

### Clang `-march` parser does not pick up new extensions

Due to issues with the ordering of extensions in `RISCVISAInfo.cpp` the search algorithm will not find entries which not inserted in the correct order. To deal with this issue the following workaround is recommended:

- Only generate patches for a single model (CoreDSL file)
- Make sure that the `arch` string always starts with an `x`, or better prefix every arch string with `xseal5`.

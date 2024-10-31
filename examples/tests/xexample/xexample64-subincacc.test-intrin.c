// Test the SubIncAcc instruction of the TUM "example" extension.
// After calling the function the value 10 should be present in
// register a0, where an integer return value would be expected
//
// Compile with the "example" extension specified:
//   clang test_subincacc.c -c --target=riscv32 -march=rv32ixexample
// then disassembly shows the new instruction:
//   llvm-objdump -d test_subincacc.o --disassembler-options=numeric

// For automated runs by llvm-lit:
// RUN: clang -c -target riscv64-unknown-elf -march=rv64xexample -o %t.o %s
// RUN: llvm-objdump --disassembler-options=numeric -d %t.o | FileCheck %s


int test_intrinsic(int a, int b, int c) {
    // CHECK: <test_intrinsic>
    // Can't rely upon specific registers being used but at least instruction should have been used
    // CHECK: xexample64.subincacc
    c = __builtin_xexample64_subincacc(a, b, c);
}

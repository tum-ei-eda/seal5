// Test the SubIncAcc instruction of the TUM "example" extension.
// After calling the function the value 10 should be present in
// register a0, where an integer return value would be expected
//
// Compile with the "example" extension specified:
//   clang test_subincacc.c -c --target=riscv32 -march=rv32ixexample
// then disassembly shows the new instruction:
//   llvm-objdump -d test_subincacc.o --disassembler-options=numeric

// For automated runs by llvm-lit:
// RUN: %clang -c -target riscv32-unknown-elf -march=rv32ixexample -o %t.o %s
// RUN: llvm-objdump --disassembler-options=numeric -d %t.o | FileCheck %s


__attribute__((naked)) void test_subincacc() {
    // Non-ISAX canary instruction, to flag an unwanted case of endian/width/compression/whatever
    // CHECK: b3 01 52 00 add x3, x4, x5
    asm("add x3, x4, x5");

    asm("li a0, 11");
    asm("li a1, 5");
    asm("li a2, 7");
    // CHECK: ab ba b5 51 cv_subincacc x21, x11, x27
    asm("cv_subincacc x21, x11, x27");
}

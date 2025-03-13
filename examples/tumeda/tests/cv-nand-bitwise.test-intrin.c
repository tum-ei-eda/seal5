// RUN: clang -c -target riscv32-unknown-elf -march=rv32ixcorevnand -o %t.o %s
// RUN: llvm-objdump --disassembler-options=numeric -d %t.o | FileCheck %s


int test_nand(int a, int b) {
    // CHECK: <test_nand>
    // Can't rely upon specific registers being used but at least instruction should have been used
    // CHECK: cv.nand.bitwise
    return __builtin_xcv_nand_bitwise(a, b);
}

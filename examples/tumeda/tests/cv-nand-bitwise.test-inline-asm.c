// RUN: clang -c -target riscv32-unknown-elf -march=rv32ixcorevnand -o %t.o %s
// RUN: llvm-objdump --disassembler-options=numeric -d %t.o | FileCheck %s

__attribute__((naked)) void test_nand() {
    // CHECK: 93b5eaab cv.nand.bitwise x21, x11, x27
    asm("cv.nand.bitwise x21, x11, x27");
}

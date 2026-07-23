// RUN: clang -c -target riscv32-unknown-elf -march=rv32ixexample -o %t.o %s
// RUN: llvm-objdump --disassembler-options=numeric -d %t.o | FileCheck %s

__attribute__((naked)) void test_subincacc() {
    // CHECK: 51b5baab xexample.subincacc x21, x11, x27
    asm("xexample.subincacc x21, x11, x27");
}

// RUN: clang -c -target riscv32-unknown-elf -march=rv32ixexample -o %t.o %s
// RUN: llvm-objdump --disassembler-options=numeric -d %t.o | FileCheck %s

__attribute__((naked)) void test_subincacc() {
    // CHECK: ab ba b5 51 xexample.subincacc x21, x11, x27
    asm("xexample.subincacc x21, x11, x27");
}

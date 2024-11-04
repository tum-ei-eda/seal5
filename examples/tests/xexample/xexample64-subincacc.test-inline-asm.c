// RUN: clang -c -target riscv64-unknown-elf -march=rv64ixexample -o %t.o %s
// RUN: llvm-objdump --disassembler-options=numeric -d %t.o | FileCheck %s

__attribute__((naked)) void test_subincacc() {
    // CHECK: ab ba b5 51 xexample64.subincacc x21, x11, x27
    asm("xexample64.subincacc x21, x11, x27");
}

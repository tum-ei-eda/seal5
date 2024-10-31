// RUN: clang -c -target riscv32-unknown-elf -march=rv32i -Xclang -target-feature -Xclang +xexample -mllvm -global-isel=1 -O3 -o %t.o %s
// RUN: llvm-objdump --mattr=+i,+xexample --disassembler-options=numeric -d %t.o | FileCheck %s

int test_subincacc(int a, int b, int c) {
    // CHECK: 0b 05 b5 2a xexample.subincacc x10, x10, x11
    return a + (b - c + 1);
}

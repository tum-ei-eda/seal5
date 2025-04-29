// RUN: clang -c -target riscv32-unknown-elf -march=rv32i -Xclang -target-feature -Xclang +xexample -mllvm -global-isel=1 -O3 -o %t.o %s
// RUN: llvm-objdump --mattr=+i,+xexample --disassembler-options=numeric -d %t.o | FileCheck %s

int test_subincacc(int a, int b, int c) {
    // CHECK: 2b 36 b5 50 xexample.subincacc x12, x10, x11
    return ((a + 1) - b) + c;
}

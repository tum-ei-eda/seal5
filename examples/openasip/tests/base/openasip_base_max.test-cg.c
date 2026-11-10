// RUN: clang -c -target riscv32-unknown-elf -march=rv32i -Xclang -target-feature -Xclang +experimental-xopenasipbase -mllvm -global-isel=1 -O3 -o %t.o %s
// RUN: llvm-objdump --mattr=+i,+experimental-xopenasipbase --disassembler-options=numeric -d %t.o | FileCheck %s

int test_max(int a, int b) {
    // CHECK: 2ab5050b openasip_base_max x10, x10, x11
    return (a > b) ? a : b;
}

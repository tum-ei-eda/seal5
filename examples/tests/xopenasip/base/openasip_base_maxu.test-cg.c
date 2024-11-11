// RUN: clang -c -target riscv32-unknown-elf -march=rv32i -Xclang -target-feature -Xclang +xopenasipbase -mllvm -global-isel=1 -O3 -o %t.o %s
// RUN: llvm-objdump --mattr=+i,+xopenasipbase --disassembler-options=numeric -d %t.o | FileCheck %s

unsigned int test_maxu(unsigned int a, unsigned int b) {
    // CHECK: 0b 05 b5 2e openasip_base_maxu x10, x10, x11
    return (a > b) ? a : b;
}

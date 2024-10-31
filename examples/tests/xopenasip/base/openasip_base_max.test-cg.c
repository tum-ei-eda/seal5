// RUN: clang -c -target riscv32-unknown-elf -march=rv32i -Xclang -target-feature -Xclang +xopenasipbase -mllvm -global-isel=1 -o %t.o %s
// RUN: llvm-objdump --mattr=+i,+xopenasipbase --disassembler-options=numeric -d %t.o | FileCheck %s

int test_max(int a, int b) {
    // CHECK: 8b 8a b5 2b openasip_base_max x21, x11, x27
    return (a > b) ? a : b;
}

// unsigned int test_max2(unsigned int a, unsigned int b) {
//     return (a > b) ? a : b;
// }

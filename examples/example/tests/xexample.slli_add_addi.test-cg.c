# Generated on Fri, 04 Jul 2025 07:56:07 +0200.
#
# This file contains the Info for generating invalid tests for the XExample 
# core architecture.



// RUN: clang -c -target riscv32-unknown-elf -march=rv32i -Xclang -target-feature -Xclang +xexample -mllvm -global-isel=1 -O3 -o %t.o %s
// RUN: llvm-objdump --mattr=+i,+xexample --disassembler-options=numeric -d %t.o | FileCheck %s

int test_slli_add_addi(int a, int b, int c) {
    // CHECK: 2b 36 b5 50 xexample.slli_add_addi x12, x10, x11
    return ((a + 1) - b) + c;
}

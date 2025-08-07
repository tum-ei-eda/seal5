# Generated on Mon, 14 Jul 2025 01:09:17 +0200.
#
# This file contains the Info for generating invalid tests for the XExample 
# core architecture.


// RUN: clang -c -target riscv32-unknown-elf -march=rv32ixexample -o %t.o %s
// RUN: llvm-objdump --disassembler-options=numeric -d %t.o | FileCheck %s

__attribute__((naked)) void test_slli_add_addi() {
    // CHECK: 57, 96, 83, 00 xexample.slli_add_addi x11, x14, x16
    asm("xexample.slli_add_addi x11, x14, x16");
}

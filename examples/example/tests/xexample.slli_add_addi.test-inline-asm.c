# Generated on Fri, 04 Jul 2025 07:56:07 +0200.
#
# This file contains the Info for generating invalid tests for the XExample 
# core architecture.


// RUN: clang -c -target riscv32-unknown-elf -march=rv32ixexample -o %t.o %s
// RUN: llvm-objdump --disassembler-options=numeric -d %t.o | FileCheck %s

__attribute__((naked)) void test_slli_add_addi() {
    // CHECK: 57, d6, 8b, 00 xexample.slli_add_addi x11, x15, x17
    asm("xexample.slli_add_addi x11, x15, x17");
}

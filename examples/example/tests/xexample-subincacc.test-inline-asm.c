# Generated on Mon, 14 Jul 2025 01:09:17 +0200.
#
# This file contains the Info for generating invalid tests for the XExample 
# core architecture.


// RUN: clang -c -target riscv32-unknown-elf -march=rv32ixexample -o %t.o %s
// RUN: llvm-objdump --disassembler-options=numeric -d %t.o | FileCheck %s

__attribute__((naked)) void test_cv_subincacc() {
    // CHECK: 2b, 35, f6, 50 xexample.subincacc x10, x12, x15
    asm("xexample.subincacc x10, x12, x15");
}

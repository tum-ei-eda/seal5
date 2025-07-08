# Generated on Tue, 08 Jul 2025 09:42:51 +0200.
#
# This file contains the Info for generating invalid tests for the XExample 
# core architecture.


// RUN: clang -c -target riscv32-unknown-elf -march=rv32ixexample -o %t.o %s
// RUN: llvm-objdump --disassembler-options=numeric -d %t.o | FileCheck %s

__attribute__((naked)) void test_cv_subincacc() {
    // CHECK: 2b, b5, 07, 51 xexample.subincacc x10, x15, x16
    asm("xexample.subincacc x10, x15, x16");
}

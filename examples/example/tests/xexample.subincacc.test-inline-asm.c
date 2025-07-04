# Generated on Fri, 04 Jul 2025 07:56:07 +0200.
#
# This file contains the Info for generating invalid tests for the XExample 
# core architecture.


// RUN: clang -c -target riscv32-unknown-elf -march=rv32ixexample -o %t.o %s
// RUN: llvm-objdump --disassembler-options=numeric -d %t.o | FileCheck %s

__attribute__((naked)) void test_cv_subincacc() {
    // CHECK: ab, 35, 17, 51 xexample.subincacc x11, x14, x17
    asm("xexample.subincacc x11, x14, x17");
}

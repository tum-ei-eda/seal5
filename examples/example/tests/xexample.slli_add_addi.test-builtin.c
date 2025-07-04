# Generated on Fri, 04 Jul 2025 07:56:07 +0200.
#
# This file contains the Info for generating invalid tests for the XExample 
# core architecture.



// RUN: clang -c -target riscv32-unknown-elf -march=rv32ixexample -o %t.o %s
// RUN: llvm-objdump --disassembler-options=numeric -d %t.o | FileCheck %s


int test_intrinsic(int a, int b, int c) {
    // CHECK: <test_intrinsic>
    // Can't rely upon specific registers being used but at least instruction should have been used
    // CHECK: xexample.slli_add_addi
    c = _builtin_riscv_xexample_{intrinsic_name}(a, b, c);
}

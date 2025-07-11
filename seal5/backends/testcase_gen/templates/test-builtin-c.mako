## SPDX-License-Identifier: Apache-2.0
##
## This file is part of the M2-ISA-R project: https://github.com/tum-ei-eda/M2-ISA-R
##
## Copyright (c) 2025 TUM Department of Electrical and Computer Engineering.
## Copyright (c) 2025 DLR-SE Department of System Evolution and Operation
\
# Generated on ${start_time}.
#
# This file contains the Info for generating invalid tests for the ${set_name} 
# core architecture.



// RUN: clang -c -target riscv${xlen}-unknown-elf -march=rv${xlen}i${arch} -o %t.o %s
// RUN: llvm-objdump --disassembler-options=numeric -d %t.o | FileCheck %s


int test_intrinsic(int a, int b, int c) {
    // CHECK: <test_intrinsic>
    // Can't rely upon specific registers being used but at least instruction should have been used
    // CHECK: ${mnemonic}
    c = _builtin_riscv_${arch}_{intrinsic_name}(a, b, c);
}

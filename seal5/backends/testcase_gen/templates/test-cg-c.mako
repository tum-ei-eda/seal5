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



// RUN: clang -c -target riscv${xlen}-unknown-elf -march=rv${xlen}i -Xclang -target-feature -Xclang +${arch} -mllvm -global-isel=1 -O3 -o %t.o %s
// RUN: llvm-objdump --mattr=+i,+${arch} --disassembler-options=numeric -d %t.o | FileCheck %s

int test_${instr_name}(int a, int b, int c) {
    // CHECK: 2b 36 b5 50 ${mnemonic} x12, x10, x11
    return ((a + 1) - b) + c;
}

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


// RUN: clang -c -target riscv${xlen}-unknown-elf -march=rv${xlen}i${set_name_lower} -o %t.o %s
// RUN: llvm-objdump --disassembler-options=numeric -d %t.o | FileCheck %s

__attribute__((naked)) void test_${instr_name}() {
    // CHECK: ${enc} ${mnemonic} ${reg_names_list}
    asm("${mnemonic} ${reg_names_list}");
}

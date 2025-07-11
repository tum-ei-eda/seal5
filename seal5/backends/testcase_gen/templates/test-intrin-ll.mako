## SPDX-License-Identifier: Apache-2.0
##
## This file is part of the M2-ISA-R project: https://github.com/tum-ei-eda/M2-ISA-R
##
## Copyright (c) 2025 TUM Department of Electrical and Computer Engineering.
## Copyright (c) 2025 DLR-SE Department of System Evolution and Operation
\
% if(${timestamp_on} == TRUE):
 Generated on ${start_time}
% endif
#
# This file contains the Info for generating invalid tests for the ${set_name} 
# core architecture.



; RUN: llc -O3 -mtriple=riscv${xlen} -mattr=+${arch) -verify-machineinstrs < %s \
; RUN:   | FileCheck %s

declare i${xlen} @llvm.riscv.${instr_name}(i${xlen}, i${xlen}, i${xlen})

define i${xlen} @${instr_name}(i${xlen} %a, i${xlen} %b, i${xlen} %c) {
; CHECK-LABEL: ${instr_name}:
; CHECK:       # %bb.0:
; CHECK-NEXT:    ${mnemonic} a0, a1, a2
; CHECK-NEXT:    ret
  %1 = call i${xlen} @llvm.riscv.${instr_name}(i${xlen} %a, i${xlen} %b, i${xlen} %c)
  ret i${xlen} %1
}

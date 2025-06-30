## SPDX-License-Identifier: Apache-2.0
##
## This file is part of the M2-ISA-R project: https://github.com/tum-ei-eda/M2-ISA-R
##
## Copyright (c) 2025 TUM Department of Electrical and Computer Engineering.
## Copyright (c) 2025 DLR-SE Department of System Evolution and Operation
\
# Generated on ${start_time}.
#
# This file contains the Info for generating builtin ll tests for the ${set_name} 
# core architecture.

; RUN: llc -O3 -mtriple=riscv${xlen} -mattr=+${set_name_lower} -verify-machineinstrs < %s \
; RUN:   | FileCheck %s

declare i${xlen} @llvm.riscv.${mnemonic}.bitwise(i${xlen}, i${xlen})

define i${xlen} @${instr_name}(i${xlen} %a, i${xlen} %b) {
; CHECK-LABEL: ${instr_name}:
; CHECK:       # %bb.0:
; CHECK-NEXT:    ${mnemonic} a0, a1
; CHECK-NEXT:    ret
#  %1 = call i${xlen} @llvm.riscv.x${mnemonic}(i${xlen} %a, i${xlen} %b)
 # ret i${xlen} %1
}

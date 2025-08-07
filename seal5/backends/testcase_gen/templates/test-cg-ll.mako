## SPDX-License-Identifier: Apache-2.0
##
## This file is part of the M2-ISA-R project: https://github.com/tum-ei-eda/M2-ISA-R
##
## Copyright (c) 2025 TUM Department of Electrical and Computer Engineering.
## Copyright (c) 2025 DLR - Institute of Systems Engineering for Future Mobility
\
# Generated on ${start_time}.
#
# This file contains the Info for generating invalid tests for the ${set_name} 
# core architecture.



; RUN: llc -O3 -mtriple=riscv${xlen} -mattr=+${arch} -verify-machineinstrs -global-isel=1 < %s \
; RUN:   | FileCheck -check-prefix=RV${xlen}I-GISEL %s

define i${xlen} @${instr_name}(i${xlen} %a, i${xlen} %b, i${xlen} %c) nounwind {
; RV${xlen}I-GISEL-LABEL: ${instr_name}:
; RV${xlen}I-GISEL:       # %bb.0:
; RV${xlen}I-GISEL-NEXT:   ${mnemonic} a2, a0, a1
  %1 = add i${xlen} %a, 1
  %2 = sub i${xlen} %1, %b
  %3 = add i${xlen} %2, %c
  ret i${xlen} %3
}

; RUN: llc -O3 -mtriple=riscv32 -mattr=+xexample -verify-machineinstrs -global-isel=1 < %s \
; RUN:   | FileCheck -check-prefix=RV32I-GISEL %s

define i32 @subincacc(i32 %a, i32 %b, i32 %c) nounwind {
; RV32I-GISEL-LABEL: subincacc:
; RV32I-GISEL:       # %bb.0:
; RV32I-GISEL-NEXT:    xexample.subincacc a2, a0, a1
  %1 = add i32 %a, 1
  %2 = sub i32 %1, %b
  %3 = add i32 %2, %c
  ret i32 %3
}

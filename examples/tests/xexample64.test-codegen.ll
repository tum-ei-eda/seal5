; RUN: llc -O0 -mtriple=riscv64 -mattr=+xexample -verify-machineinstrs < %s \
; RUN:   | FileCheck -check-prefix=RV64I %s

define i32 @subincacc(i64 %a, i64 %b, i64 %c) nounwind {
; RV64IC-LABEL: subincacc:
; RV64IC:       # %bb.0:
; RV64IC-NEXT:    xrv.nand a0, a1, a0
; RV64IC-NEXT:    ret
  %1 = sub i64 %a, %b
  %2 = add i64 %1, 1
  %3 = add i64 %2, %c
  ret i64 %3
}

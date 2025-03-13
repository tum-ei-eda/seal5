; RUN: llc -O3 -mtriple=riscv64 -mattr=+xexample -verify-machineinstrs -global-isel=1 < %s \
; RUN:   | FileCheck -check-prefix=RV64I %s

define i64 @subincacc(i64 %a, i64 %b, i64 %c) nounwind {
; RV64I-LABEL: subincacc:
; RV64I:       # %bb.0:
; RV64I-NEXT:    xexample64.subincacc a2, a0, a1
  %1 = add i64 %a, 1
  ; %2 = sub i64 %b, %1
  %2 = sub i64 %1, %b
  %3 = add i64 %2, %c
  ret i64 %3
}

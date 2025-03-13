; RUN: llc -O0 -mtriple=riscv32 -mattr=+c,+xrvc -verify-machineinstrs -global-isel=1 < %s \
; RUN:   | FileCheck -check-prefix=RV32IC %s

define i32 @nandi(i32 %a) nounwind {
; RV32IC-LABEL: nandi:
; RV32IC:       # %bb.0:
; RV32IC-NEXT:    xrv.nandi a0, a0, 14
; RV32IC-NEXT:    ret
  %1 = and i32 %a, 14
  %2 = xor i32 %1, -1
  ret i32 %2
}

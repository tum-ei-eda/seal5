; RUN: llc -O0 -mtriple=riscv32 -mattr=+c,+xrvc -verify-machineinstrs < %s \
; RUN:   | FileCheck -check-prefix=RV32IC %s

define i32 @nand(i32 %a, i32 %b) nounwind {
; RV32IC-LABEL: nand:
; RV32IC:       # %bb.0:
; RV32IC-NEXT:    xrv.nand a0, a1, a0
; RV32IC-NEXT:    ret
  %1 = and i32 %a, %b
  %2 = xor i32 %1, -1
  ret i32 %2
}

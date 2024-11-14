; RUN: llc -O3 -mtriple=riscv32 -mattr=+xcorevnand -verify-machineinstrs -global-isel=1 < %s \
; RUN:   | FileCheck %s

define i32 @nand(i32 %a, i32 %b) nounwind {
; CHECK-LABEL: nand:
; CHECK:       # %bb.0:
; CHECK-NEXT:    cv.nand.bitwise a0, a1, a0
  %1 = and i32 %a, %b
  %2 = xor i32 %1, -1
  ret i32 %2
}

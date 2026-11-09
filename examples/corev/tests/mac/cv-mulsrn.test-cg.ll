; RUN: llc -O0 -mtriple=riscv32 -mattr=+m,+xcorevmac -verify-machineinstrs -global-isel=1 -global-isel-abort=1 < %s \
; RUN:   | FileCheck %s

define i32 @mulsRN(i32 %a, i32 %b) {
; CHECK-LABEL: mulsRN:
; CHECK: seal5.cv.mulsrn
; CHECK: ret
  %1 = shl i32 %a, 16
  %2 = ashr i32 %1, 16
  %3 = shl i32 %b, 16
  %4 = ashr i32 %3, 16
  %5 = mul i32 %2, %4
  %6 = add i32 %5, 16
  %7 = ashr i32 %6, 5
  ret i32 %7
}

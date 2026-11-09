; RUN: llc -O0 -mtriple=riscv32 -mattr=+m,+xcorevmac -verify-machineinstrs -global-isel=1 -global-isel-abort=1 < %s \
; RUN:   | FileCheck %s

define i32 @mulhhuRN(i32 %a, i32 %b) {
; CHECK-LABEL: mulhhuRN:
; CHECK: seal5.cv.mulhhurn
; CHECK: ret
  %1 = lshr i32 %a, 16
  %2 = lshr i32 %b, 16
  %3 = mul i32 %1, %2
  %4 = add i32 %3, 16
  %5 = lshr i32 %4, 5
  ret i32 %5
}

; RUN: llc -O0 -mtriple=riscv32 -mattr=+m,+xcorevalu -verify-machineinstrs -global-isel=1 -global-isel-abort=1 < %s \
; RUN:   | FileCheck %s

define i32 @adduRN(i32 %a, i32 %b) {
; CHECK-LABEL: adduRN:
; CHECK: seal5.cv.adduRN
; CHECK: ret
  %1 = add i32 %a, %b
  %2 = add i32 %1, 16
  %3 = lshr i32 %2, 5
  ret i32 %3
}

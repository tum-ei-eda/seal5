; RUN: llc -O0 -mtriple=riscv32 -mattr=+m,+xcorevalu -verify-machineinstrs -global-isel=1 -global-isel-abort=1 < %s \
; RUN:   | FileCheck %s

define i32 @subuRNr(i32 %a, i32 %b, i32 %c) {
; CHECK-LABEL: subuRNr:
; CHECK: seal5.cv.subuRNr
; CHECK: ret
  %shift_mask = and i32 %c, 31
  %1 = sub i32 %a, %b
  %2 = shl i32 1, %shift_mask
  %3 = lshr i32 %2, 1
  %4 = add i32 %1, %3
  %5 = lshr i32 %4, %shift_mask
  ret i32 %5
}

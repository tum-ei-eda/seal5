; RUN: llc -O0 -mtriple=riscv32 -mattr=+m,+xcorevalu -verify-machineinstrs -global-isel=1 -global-isel-abort=1 < %s \
; RUN:   | FileCheck %s

define i32 @subuRN(i32 %a, i32 %b) {
; CHECK-LABEL: subuRN:
; CHECK: seal5.cv.subuRN
; CHECK: ret
  %1 = sub i32 %a, %b
  %2 = add i32 %1, 16
  %3 = lshr i32 %2, 5
  ret i32 %3
}

; RUN: llc -O0 -mtriple=riscv32 -mattr=+m,+xcorevalu -verify-machineinstrs -global-isel=1 -global-isel-abort=1 < %s \
; RUN:   | FileCheck %s

define i32 @exths(i16 %a) {
; CHECK-LABEL: exths:
; CHECK: seal5.cv.exths
; CHECK: ret
  %1 = sext i16 %a to i32
  ret i32 %1
}

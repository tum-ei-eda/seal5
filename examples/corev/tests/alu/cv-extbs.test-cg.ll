; RUN: llc -O0 -mtriple=riscv32 -mattr=+m,+xcorevalu -verify-machineinstrs -global-isel=1 -global-isel-abort=1 < %s \
; RUN:   | FileCheck %s

define i32 @extbs(i8 %a) {
; CHECK-LABEL: extbs:
; CHECK: seal5.cv.extbs
; CHECK: ret
  %1 = sext i8 %a to i32
  ret i32 %1
}

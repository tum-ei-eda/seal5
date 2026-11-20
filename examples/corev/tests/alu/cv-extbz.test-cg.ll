; RUN: llc -O0 -mtriple=riscv32 -mattr=+m,+xcorevalu -verify-machineinstrs -global-isel=1 -global-isel-abort=1 < %s \
; RUN:   | FileCheck %s

define i32 @extbz(i8 %a) {
; CHECK-LABEL: extbz:
; CHECK: seal5.cv.extbz
; CHECK: ret
  %1 = zext i8 %a to i32
  ret i32 %1
}

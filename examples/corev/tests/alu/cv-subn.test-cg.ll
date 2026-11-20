; RUN: llc -O0 -mtriple=riscv32 -mattr=+m,+xcorevalu -verify-machineinstrs -global-isel=1 -global-isel-abort=1 < %s \
; RUN:   | FileCheck %s

define i32 @subN(i32 %a, i32 %b) {
; CHECK-LABEL: subN:
; CHECK: seal5.cv.subN
; CHECK: ret
  %1 = sub i32 %a, %b
  %2 = ashr i32 %1, 5
  ret i32 %2
}

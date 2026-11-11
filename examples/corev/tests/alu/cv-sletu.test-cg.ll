; RUN: llc -O0 -mtriple=riscv32 -mattr=+m,+xcorevalu -verify-machineinstrs -global-isel=1 -global-isel-abort=1 < %s \
; RUN:   | FileCheck %s

define i1 @sletu(i32 %a, i32 %b) {
; CHECK-LABEL: sletu:
; CHECK: seal5.cv.sletu
; CHECK: ret
  %1 = icmp ule i32 %a, %b
  ret i1 %1
}

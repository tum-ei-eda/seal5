; RUN: llc -O0 -mtriple=riscv32 -mattr=+m,+xcorevalu -verify-machineinstrs -global-isel=1 -global-isel-abort=1 < %s \
; RUN:   | FileCheck %s

define i1 @slet(i32 %a, i32 %b) {
; CHECK-LABEL: slet:
; CHECK: seal5.cv.slet
; CHECK: ret
  %1 = icmp sle i32 %a, %b
  ret i1 %1
}

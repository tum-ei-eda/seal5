; NOTE: Assertions have been autogenerated by utils/update_llc_test_checks.py
; RUN: llc -O0 -mtriple=riscv32 -mattr=+m,+xcorevalu -verify-machineinstrs -global-isel=1 < %s \
; RUN:   | FileCheck %s --check-prefixes=CHECK,CHECK-GISEL

define i1 @sleu(i32 %a, i32 %b) {
; CHECK-LABEL: sle:
; CHECK:       # %bb.0:
; CHECK-GISEL-NEXT:    seal5.cv.sleu a0, a0, a1
; CHECK-NEXT:    ret
  %1 = icmp sle i32 %a, %b
  ret i1 %1
}

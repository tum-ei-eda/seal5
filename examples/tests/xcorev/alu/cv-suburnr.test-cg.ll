; NOTE: Assertions have been autogenerated by utils/update_llc_test_checks.py
; RUN: llc -O0 -mtriple=riscv32 -mattr=+m,+xcorevalu -verify-machineinstrs -global-isel=1 < %s \
; RUN:   | FileCheck %s --check-prefixes=CHECK,CHECK-GISEL

define i32 @subuRNr(i32 %a, i32 %b, i32 %c) {
; CHECK-LABEL: subuRNr:
; CHECK:       # %bb.0:
; CHECK-GISEL-NEXT:    seal5.cv.subuRNr a0, a1, a2
; CHECK-NEXT:    ret
  %1 = sub i32 %a, %b
  %2 = shl i32 1, %c
  %3 = lshr i32 %2, 1
  %4 = add i32 %1, %3
  %5 = lshr i32 %4, %c
  ret i32 %5
}
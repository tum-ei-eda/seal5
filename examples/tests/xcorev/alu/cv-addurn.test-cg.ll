; NOTE: Assertions have been autogenerated by utils/update_llc_test_checks.py
; RUN: llc -O0 -mtriple=riscv32 -mattr=+m,+xcorevalu -verify-machineinstrs -global-isel=1 < %s \
; RUN:   | FileCheck %s --check-prefixes=CHECK,CHECK-GISEL

define i32 @adduRN(i32 %a, i32 %b) {
; CHECK-LABEL: adduRN:
; CHECK:       # %bb.0:
; CHECK-GISEL-NEXT:    seal5.cv.adduRN a0, a0, a1, 5
; CHECK-NEXT:    ret
  %1 = add i32 %a, %b
  %2 = add i32 %1, 16
  %3 = lshr i32 %2, 5
  ret i32 %3
}
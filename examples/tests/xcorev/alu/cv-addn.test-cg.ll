; NOTE: Assertions have been autogenerated by utils/update_llc_test_checks.py
; RUN: llc -O0 -mtriple=riscv32 -mattr=+m,+xcorevalu -verify-machineinstrs -global-isel=1 < %s \
; RUN:   | FileCheck %s --check-prefixes=CHECK,CHECK-GISEL

define i32 @addN(i32 %a, i32 %b) {
; CHECK-LABEL: addN:
; CHECK:       # %bb.0:
; CHECK-GISEL-NEXT:    seal5.cv.addN a0, a1, a0, 5
; CHECK-NEXT:    ret
  %1 = add i32 %a, %b
  %2 = ashr i32 %1, 5
  ret i32 %2
}

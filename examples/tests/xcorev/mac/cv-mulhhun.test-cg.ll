; NOTE: Assertions have been autogenerated by utils/update_llc_test_checks.py
; RUN: llc -O0 -mtriple=riscv32 -mattr=+m,+xcorevmac -verify-machineinstrs -global-isel=1 < %s \
; RUN:   | FileCheck %s --check-prefixes=CHECK,CHECK-GISEL

define i32 @mulhhuN(i32 %a, i32 %b) {
; CHECK-LABEL: mulhhuN:
; CHECK:       # %bb.0:
; CHECK-GISEL-NEXT:    seal5.cv.mulhhun a0, a0, a1, 5
; CHECK-NEXT:    ret
  %1 = lshr i32 %a, 16
  %2 = lshr i32 %b, 16
  %3 = mul i32 %1, %2
  %4 = lshr i32 %3, 5
  ret i32 %4
}

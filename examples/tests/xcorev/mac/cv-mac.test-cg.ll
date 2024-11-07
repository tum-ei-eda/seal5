; NOTE: Assertions have been autogenerated by utils/update_llc_test_checks.py
; RUN: llc -O3 -mtriple=riscv32 -mattr=+m,+xcorevmac -verify-machineinstrs -global-isel=1 < %s \
; RUN:   | FileCheck %s --check-prefixes=CHECK,CHECK-GISEL

define i32 @mac(i32 %a, i32 %b, i32 %c) {
; CHECK-LABEL: mac:
; CHECK:       # %bb.0:
; CHECK-GISEL-NEXT:    seal5.cv.mac a2, a1, a0
; CHECK-NEXT:    mv a0, a2
; CHECK-NEXT:    ret
  %1 = mul i32 %a, %b
  %2 = add i32 %1, %c
  ret i32 %2
}
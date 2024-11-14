; NOTE: Assertions have been autogenerated by utils/update_llc_test_checks.py
; RUN: llc -O0 -mtriple=riscv32 -mattr=+m,+xcorevalu -verify-machineinstrs -global-isel=1 < %s \
; RUN:   | FileCheck %s --check-prefixes=CHECK,CHECK-GISEL

declare i32 @llvm.umin.i32(i32, i32)
declare i32 @llvm.umax.i32(i32, i32)

define i32 @clipur(i32 %a, i32 %b) {
; CHECK-LABEL: clipur:
; CHECK:       # %bb.0:
; CHECK-GISEL-NEXT:    seal5.cv.clipur a0, a0, a1
; CHECK-NEXT:    ret
  %1 = call i32 @llvm.smax.i32(i32 %a, i32 0)
  %2 = call i32 @llvm.smin.i32(i32 %1, i32 %b)
  ret i32 %2
}

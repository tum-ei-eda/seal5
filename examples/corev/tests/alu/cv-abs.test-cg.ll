; NOTE: Assertions have been autogenerated by utils/update_llc_test_checks.py
; RUN: llc -O0 -mtriple=riscv32 -mattr=+m,+xcorevalu -verify-machineinstrs -global-isel=1 < %s \
; RUN:   | FileCheck %s --check-prefixes=CHECK,CHECK-GISEL

declare i32 @llvm.abs.i32(i32, i1)

define i32 @abs(i32 %a) {
; CHECK-LABEL: abs:
; CHECK:       # %bb.0:
; CHECK-GISEL-NEXT:    seal5.cv.abs a0, a0
; CHECK-NEXT:    ret
  %1 = call i32 @llvm.abs.i32(i32 %a, i1 false)
  ret i32 %1
}

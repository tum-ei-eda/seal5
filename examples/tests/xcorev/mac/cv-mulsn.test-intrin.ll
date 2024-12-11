; NOTE: Assertions have been autogenerated by utils/update_llc_test_checks.py
; RUN: llc -mtriple=riscv32 -mattr=+m,+xcorevmac -verify-machineinstrs < %s \
; RUN:   | FileCheck %s

declare i32 @llvm.riscv.xcorevmac.mac.mulsn(i32, i32, i32)

define i32 @test_mulsn(i32 %a, i32 %b, i32 %c) {
; CHECK-LABEL: test_mulsn:
; CHECK:       # %bb.0:
; CHECK-NEXT:    seal5.cv.mulsn a2, a0, a1
; CHECK-NEXT:    mv a0, a2
; CHECK-NEXT:    ret
  %1 = call i32 @llvm.riscv.xcorevmac.mac.mulsn(i32 %a, i32 %b, i32 %c)
  ret i32 %1
}

; RUN: llc -mtriple=riscv32 -mattr=+m,+xcorevsimd -verify-machineinstrs %s -o - | FileCheck %s

declare i32 @llvm.riscv.xcorevsimd.simd.or.h.SC(i32, i32)

define i32 @cv_or_sc_h_0(i32 %a0, i32 %a1) {
; CHECK-LABEL: cv_or_sc_h_0:
; CHECK: seal5.cv.or.sc.h
  %result = call i32 @llvm.riscv.xcorevsimd.simd.or.h.SC(i32 %a0, i32 %a1)
  ret i32 %result
}

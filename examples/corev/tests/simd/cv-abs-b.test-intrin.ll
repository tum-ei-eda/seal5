; RUN: llc -mtriple=riscv32 -mattr=+m,+xcorevsimd -verify-machineinstrs %s -o - | FileCheck %s

declare i32 @llvm.riscv.xcorevsimd.simd.abs.b(i32)

define i32 @cv_abs_b_0(i32 %a0) {
; CHECK-LABEL: cv_abs_b_0:
; CHECK: seal5.cv.abs.b
  %result = call i32 @llvm.riscv.xcorevsimd.simd.abs.b(i32 %a0)
  ret i32 %result
}

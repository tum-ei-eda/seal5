; RUN: llc -mtriple=riscv32 -mattr=+m,+xcorevsimd -verify-machineinstrs %s -o - | FileCheck %s

declare i32 @llvm.riscv.xcorevsimd.simd.maxu.b(i32, i32)

define i32 @cv_maxu_b_0(i32 %a0, i32 %a1) {
; CHECK-LABEL: cv_maxu_b_0:
; CHECK: seal5.cv.maxu.b
  %result = call i32 @llvm.riscv.xcorevsimd.simd.maxu.b(i32 %a0, i32 %a1)
  ret i32 %result
}

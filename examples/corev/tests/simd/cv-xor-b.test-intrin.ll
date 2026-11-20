; RUN: llc -mtriple=riscv32 -mattr=+m,+xcorevsimd -verify-machineinstrs %s -o - | FileCheck %s

declare i32 @llvm.riscv.xcorevsimd.simd.xor.b(i32, i32)

define i32 @cv_xor_b_0(i32 %a0, i32 %a1) {
; CHECK-LABEL: cv_xor_b_0:
; CHECK: seal5.cv.xor.b
  %result = call i32 @llvm.riscv.xcorevsimd.simd.xor.b(i32 %a0, i32 %a1)
  ret i32 %result
}

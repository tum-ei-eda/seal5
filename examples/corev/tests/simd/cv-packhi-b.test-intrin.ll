; RUN: llc -mtriple=riscv32 -mattr=+m,+xcorevsimd -verify-machineinstrs %s -o - | FileCheck %s

declare i32 @llvm.riscv.xcorevsimd.simd.packhi.b(i32, i32, i32)

define i32 @cv_packhi_b_0(i32 %a0, i32 %a1, i32 %a2) {
; CHECK-LABEL: cv_packhi_b_0:
; CHECK: seal5.cv.packhi.b
  %result = call i32 @llvm.riscv.xcorevsimd.simd.packhi.b(i32 %a0, i32 %a1, i32 %a2)
  ret i32 %result
}

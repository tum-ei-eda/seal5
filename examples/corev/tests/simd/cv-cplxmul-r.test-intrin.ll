; RUN: llc -mtriple=riscv32 -mattr=+m,+xcorevsimd -verify-machineinstrs %s -o - | FileCheck %s

declare i32 @llvm.riscv.xcorevsimd.simd.cplxmul.r(i32, i32, i32)

define i32 @cv_cplxmul_r_0(i32 %a0, i32 %a1, i32 %a2) {
; CHECK-LABEL: cv_cplxmul_r_0:
; CHECK: seal5.cv.cplxmul.r
  %result = call i32 @llvm.riscv.xcorevsimd.simd.cplxmul.r(i32 %a0, i32 %a1, i32 %a2)
  ret i32 %result
}

; RUN: llc -mtriple=riscv32 -mattr=+m,+xcorevsimd -verify-machineinstrs %s -o - | FileCheck %s

declare i32 @llvm.riscv.xcorevsimd.simd.cplxconj(i32)

define i32 @cv_cplxconj_0(i32 %a0) {
; CHECK-LABEL: cv_cplxconj_0:
; CHECK: seal5.cv.cplxconj
  %result = call i32 @llvm.riscv.xcorevsimd.simd.cplxconj(i32 %a0)
  ret i32 %result
}

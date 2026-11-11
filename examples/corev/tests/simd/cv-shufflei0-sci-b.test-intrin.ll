; RUN: llc -mtriple=riscv32 -mattr=+m,+xcorevsimd -verify-machineinstrs %s -o - | FileCheck %s

declare i32 @llvm.riscv.xcorevsimd.simd.shuffle0.sci.b(i32, i32)

define i32 @cv_shufflei0_sci_b_0(i32 %a0) {
; CHECK-LABEL: cv_shufflei0_sci_b_0:
; CHECK: seal5.cv.shuffleI0.sci.b
  %result = call i32 @llvm.riscv.xcorevsimd.simd.shuffle0.sci.b(i32 %a0, i32 0)
  ret i32 %result
}

define i32 @cv_shufflei0_sci_b_1(i32 %a0) {
; CHECK-LABEL: cv_shufflei0_sci_b_1:
; CHECK: seal5.cv.shuffleI0.sci.b
  %result = call i32 @llvm.riscv.xcorevsimd.simd.shuffle0.sci.b(i32 %a0, i32 1)
  ret i32 %result
}

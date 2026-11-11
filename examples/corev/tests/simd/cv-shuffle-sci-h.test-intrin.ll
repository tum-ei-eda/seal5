; RUN: llc -mtriple=riscv32 -mattr=+m,+xcorevsimd -verify-machineinstrs %s -o - | FileCheck %s

declare i32 @llvm.riscv.xcorevsimd.simd.shuffle.sci.h(i32, i32)

define i32 @cv_shuffle_sci_h_0(i32 %a0) {
; CHECK-LABEL: cv_shuffle_sci_h_0:
; CHECK: seal5.cv.shuffle.sci.h
  %result = call i32 @llvm.riscv.xcorevsimd.simd.shuffle.sci.h(i32 %a0, i32 0)
  ret i32 %result
}

define i32 @cv_shuffle_sci_h_1(i32 %a0) {
; CHECK-LABEL: cv_shuffle_sci_h_1:
; CHECK: seal5.cv.shuffle.sci.h
  %result = call i32 @llvm.riscv.xcorevsimd.simd.shuffle.sci.h(i32 %a0, i32 1)
  ret i32 %result
}

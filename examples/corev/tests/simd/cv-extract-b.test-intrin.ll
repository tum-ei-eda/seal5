; RUN: llc -mtriple=riscv32 -mattr=+m,+xcorevsimd -verify-machineinstrs %s -o - | FileCheck %s

declare i32 @llvm.riscv.xcorevsimd.simd.extract.b(i32, i32)

define i32 @cv_extract_b_0(i32 %a0) {
; CHECK-LABEL: cv_extract_b_0:
; CHECK: seal5.cv.extract.b
  %result = call i32 @llvm.riscv.xcorevsimd.simd.extract.b(i32 %a0, i32 0)
  ret i32 %result
}

define i32 @cv_extract_b_1(i32 %a0) {
; CHECK-LABEL: cv_extract_b_1:
; CHECK: seal5.cv.extract.b
  %result = call i32 @llvm.riscv.xcorevsimd.simd.extract.b(i32 %a0, i32 1)
  ret i32 %result
}

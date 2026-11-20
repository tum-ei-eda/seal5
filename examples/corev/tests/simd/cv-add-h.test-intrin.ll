; RUN: llc -mtriple=riscv32 -mattr=+m,+xcorevsimd -verify-machineinstrs %s -o - | FileCheck %s

declare i32 @llvm.riscv.xcorevsimd.simd.add.h(i32, i32)

define i32 @cv_add_h_0(i32 %a0, i32 %a1) {
; CHECK-LABEL: cv_add_h_0:
; CHECK: seal5.cv.add.h
  %result = call i32 @llvm.riscv.xcorevsimd.simd.add.h(i32 %a0, i32 %a1)
  ret i32 %result
}

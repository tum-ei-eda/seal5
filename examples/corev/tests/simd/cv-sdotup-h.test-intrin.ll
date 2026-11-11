; RUN: llc -mtriple=riscv32 -mattr=+m,+xcorevsimd -verify-machineinstrs %s -o - | FileCheck %s

declare i32 @llvm.riscv.xcorevsimd.simd.sdotup.h(i32, i32, i32)

define i32 @cv_sdotup_h_0(i32 %a0, i32 %a1, i32 %a2) {
; CHECK-LABEL: cv_sdotup_h_0:
; CHECK: seal5.cv.sdotup.h
  %result = call i32 @llvm.riscv.xcorevsimd.simd.sdotup.h(i32 %a0, i32 %a1, i32 %a2)
  ret i32 %result
}

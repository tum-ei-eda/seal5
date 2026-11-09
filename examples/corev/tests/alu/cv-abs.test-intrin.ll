; RUN: llc -mtriple=riscv32 -mattr=+m,+xcorevalu -verify-machineinstrs %s -o - | FileCheck %s

declare i32 @llvm.riscv.xcorevalu.alu.abs(i32)

define i32 @cv_abs_0(i32 %a0) {
; CHECK-LABEL: cv_abs_0:
; CHECK: seal5.cv.abs
  %result = call i32 @llvm.riscv.xcorevalu.alu.abs(i32 %a0)
  ret i32 %result
}

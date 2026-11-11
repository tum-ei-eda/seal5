; RUN: llc -mtriple=riscv32 -mattr=+m,+xcorevalu -verify-machineinstrs %s -o - | FileCheck %s

declare i32 @llvm.riscv.xcorevalu.alu.exths(i32)

define i32 @cv_exths_0(i32 %a0) {
; CHECK-LABEL: cv_exths_0:
; CHECK: seal5.cv.exths
  %result = call i32 @llvm.riscv.xcorevalu.alu.exths(i32 %a0)
  ret i32 %result
}

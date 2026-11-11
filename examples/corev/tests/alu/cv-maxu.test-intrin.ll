; RUN: llc -mtriple=riscv32 -mattr=+m,+xcorevalu -verify-machineinstrs %s -o - | FileCheck %s

declare i32 @llvm.riscv.xcorevalu.alu.maxu(i32, i32)

define i32 @cv_maxu_0(i32 %a0, i32 %a1) {
; CHECK-LABEL: cv_maxu_0:
; CHECK: seal5.cv.maxu
  %result = call i32 @llvm.riscv.xcorevalu.alu.maxu(i32 %a0, i32 %a1)
  ret i32 %result
}

; RUN: llc -mtriple=riscv32 -mattr=+m,+xcorevalu -verify-machineinstrs %s -o - | FileCheck %s

declare i32 @llvm.riscv.xcorevalu.alu.subnr(i32, i32, i32)

define i32 @cv_subnr_0(i32 %a0, i32 %a1, i32 %a2) {
; CHECK-LABEL: cv_subnr_0:
; CHECK: seal5.cv.subNr
  %result = call i32 @llvm.riscv.xcorevalu.alu.subnr(i32 %a0, i32 %a1, i32 %a2)
  ret i32 %result
}

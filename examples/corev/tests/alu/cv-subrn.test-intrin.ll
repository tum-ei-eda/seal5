; RUN: llc -mtriple=riscv32 -mattr=+m,+xcorevalu -verify-machineinstrs %s -o - | FileCheck %s

declare i32 @llvm.riscv.xcorevalu.alu.subrn(i32, i32, i32)

define i32 @cv_subrn_0(i32 %a0, i32 %a1) {
; CHECK-LABEL: cv_subrn_0:
; CHECK: seal5.cv.subRN
  %result = call i32 @llvm.riscv.xcorevalu.alu.subrn(i32 %a0, i32 %a1, i32 0)
  ret i32 %result
}

define i32 @cv_subrn_1(i32 %a0, i32 %a1) {
; CHECK-LABEL: cv_subrn_1:
; CHECK: seal5.cv.subRN
  %result = call i32 @llvm.riscv.xcorevalu.alu.subrn(i32 %a0, i32 %a1, i32 1)
  ret i32 %result
}

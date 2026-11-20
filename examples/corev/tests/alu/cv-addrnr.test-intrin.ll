; RUN: llc -mtriple=riscv32 -mattr=+m,+xcorevalu -verify-machineinstrs %s -o - | FileCheck %s

declare i32 @llvm.riscv.xcorevalu.alu.addrnr(i32, i32, i32)

define i32 @cv_addrnr_0(i32 %a0, i32 %a1, i32 %a2) {
; CHECK-LABEL: cv_addrnr_0:
; CHECK: seal5.cv.addRNr
  %result = call i32 @llvm.riscv.xcorevalu.alu.addrnr(i32 %a0, i32 %a1, i32 %a2)
  ret i32 %result
}

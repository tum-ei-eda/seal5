; RUN: llc -mtriple=riscv32 -mattr=+m,+xcorevalu -verify-machineinstrs %s -o - | FileCheck %s

declare i32 @llvm.riscv.xcorevalu.alu.clipr(i32, i32)

define i32 @cv_clipr_0(i32 %a0, i32 %a1) {
; CHECK-LABEL: cv_clipr_0:
; CHECK: seal5.cv.clipr
  %result = call i32 @llvm.riscv.xcorevalu.alu.clipr(i32 %a0, i32 %a1)
  ret i32 %result
}

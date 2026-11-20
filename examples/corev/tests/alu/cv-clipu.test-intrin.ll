; RUN: llc -mtriple=riscv32 -mattr=+m,+xcorevalu -verify-machineinstrs %s -o - | FileCheck %s

declare i32 @llvm.riscv.xcorevalu.alu.clipu(i32, i32)

define i32 @cv_clipu_0(i32 %a0) {
; CHECK-LABEL: cv_clipu_0:
; CHECK: seal5.cv.clipu
  %result = call i32 @llvm.riscv.xcorevalu.alu.clipu(i32 %a0, i32 0)
  ret i32 %result
}

define i32 @cv_clipu_1(i32 %a0) {
; CHECK-LABEL: cv_clipu_1:
; CHECK: seal5.cv.clipu
  %result = call i32 @llvm.riscv.xcorevalu.alu.clipu(i32 %a0, i32 1)
  ret i32 %result
}

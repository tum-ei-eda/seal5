; RUN: llc -mtriple=riscv32 -mattr=+m,+xcorevbitmanip -verify-machineinstrs %s -o - | FileCheck %s

declare i32 @llvm.riscv.xcorevbitmanip.bitmanip.extractur(i32, i32)

define i32 @cv_extractur_0(i32 %a0, i32 %a1) {
; CHECK-LABEL: cv_extractur_0:
; CHECK: seal5.cv.extractur
  %result = call i32 @llvm.riscv.xcorevbitmanip.bitmanip.extractur(i32 %a0, i32 %a1)
  ret i32 %result
}

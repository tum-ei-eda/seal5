; RUN: llc -mtriple=riscv32 -mattr=+m,+xcorevbitmanip -verify-machineinstrs %s -o - | FileCheck %s

declare i32 @llvm.riscv.xcorevbitmanip.bitmanip.ff1(i32)

define i32 @cv_ff1_0(i32 %a0) {
; CHECK-LABEL: cv_ff1_0:
; CHECK: seal5.cv.ff1
  %result = call i32 @llvm.riscv.xcorevbitmanip.bitmanip.ff1(i32 %a0)
  ret i32 %result
}

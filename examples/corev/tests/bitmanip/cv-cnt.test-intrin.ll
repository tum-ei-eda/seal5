; RUN: llc -mtriple=riscv32 -mattr=+m,+xcorevbitmanip -verify-machineinstrs %s -o - | FileCheck %s

declare i32 @llvm.riscv.xcorevbitmanip.bitmanip.cnt(i32)

define i32 @cv_cnt_0(i32 %a0) {
; CHECK-LABEL: cv_cnt_0:
; CHECK: seal5.cv.cnt
  %result = call i32 @llvm.riscv.xcorevbitmanip.bitmanip.cnt(i32 %a0)
  ret i32 %result
}

; RUN: llc -mtriple=riscv32 -mattr=+m,+xcorevbitmanip -verify-machineinstrs %s -o - | FileCheck %s

declare i32 @llvm.riscv.xcorevbitmanip.bitmanip.ror(i32, i32)

define i32 @cv_ror_0(i32 %a0, i32 %a1) {
; CHECK-LABEL: cv_ror_0:
; CHECK: seal5.cv.ror
  %result = call i32 @llvm.riscv.xcorevbitmanip.bitmanip.ror(i32 %a0, i32 %a1)
  ret i32 %result
}

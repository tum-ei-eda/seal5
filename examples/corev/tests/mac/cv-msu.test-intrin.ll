; RUN: llc -mtriple=riscv32 -mattr=+m,+xcorevmac -verify-machineinstrs %s -o - | FileCheck %s

declare i32 @llvm.riscv.xcorevmac.mac.msu(i32, i32, i32)

define i32 @cv_msu_0(i32 %a0, i32 %a1, i32 %a2) {
; CHECK-LABEL: cv_msu_0:
; CHECK: seal5.cv.msu
  %result = call i32 @llvm.riscv.xcorevmac.mac.msu(i32 %a0, i32 %a1, i32 %a2)
  ret i32 %result
}

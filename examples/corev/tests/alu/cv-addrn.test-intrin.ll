; RUN: llc -mtriple=riscv32 -mattr=+m,+xcorevalu -verify-machineinstrs %s -o - | FileCheck %s

declare i32 @llvm.riscv.xcorevalu.alu.addrn(i32, i32, i32)

define i32 @cv_addrn_0(i32 %a0, i32 %a1) {
; CHECK-LABEL: cv_addrn_0:
; CHECK: seal5.cv.addRN
  %result = call i32 @llvm.riscv.xcorevalu.alu.addrn(i32 %a0, i32 %a1, i32 0)
  ret i32 %result
}

define i32 @cv_addrn_1(i32 %a0, i32 %a1) {
; CHECK-LABEL: cv_addrn_1:
; CHECK: seal5.cv.addRN
  %result = call i32 @llvm.riscv.xcorevalu.alu.addrn(i32 %a0, i32 %a1, i32 1)
  ret i32 %result
}

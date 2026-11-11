; RUN: llc -mtriple=riscv32 -mattr=+m,+xcorevmac -verify-machineinstrs %s -o - | FileCheck %s

declare i32 @llvm.riscv.xcorevmac.mac.machhsrn(i32, i32, i32, i32)

define i32 @cv_machhsrn_0(i32 %a0, i32 %a1, i32 %a2) {
; CHECK-LABEL: cv_machhsrn_0:
; CHECK: seal5.cv.machhsrn
  %result = call i32 @llvm.riscv.xcorevmac.mac.machhsrn(i32 %a0, i32 %a1, i32 %a2, i32 0)
  ret i32 %result
}

define i32 @cv_machhsrn_1(i32 %a0, i32 %a1, i32 %a2) {
; CHECK-LABEL: cv_machhsrn_1:
; CHECK: seal5.cv.machhsrn
  %result = call i32 @llvm.riscv.xcorevmac.mac.machhsrn(i32 %a0, i32 %a1, i32 %a2, i32 1)
  ret i32 %result
}

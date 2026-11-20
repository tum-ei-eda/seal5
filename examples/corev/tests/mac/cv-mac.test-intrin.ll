; RUN: llc -mtriple=riscv32 -mattr=+m,+xcorevmac -verify-machineinstrs %s -o - | FileCheck %s

declare i32 @llvm.riscv.xcorevmac.mac.mac(i32, i32, i32)

define i32 @cv_mac_0(i32 %a0, i32 %a1, i32 %a2) {
; CHECK-LABEL: cv_mac_0:
; CHECK: seal5.cv.mac
  %result = call i32 @llvm.riscv.xcorevmac.mac.mac(i32 %a0, i32 %a1, i32 %a2)
  ret i32 %result
}

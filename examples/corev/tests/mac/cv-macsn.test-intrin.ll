; RUN: llc -mtriple=riscv32 -mattr=+m,+xcorevmac -verify-machineinstrs %s -o - | FileCheck %s

declare i32 @llvm.riscv.xcorevmac.mac.macsn(i32, i32, i32, i32)

define i32 @cv_macsn_0(i32 %a0, i32 %a1, i32 %a2) {
; CHECK-LABEL: cv_macsn_0:
; CHECK: seal5.cv.macsn
  %result = call i32 @llvm.riscv.xcorevmac.mac.macsn(i32 %a0, i32 %a1, i32 %a2, i32 0)
  ret i32 %result
}

define i32 @cv_macsn_1(i32 %a0, i32 %a1, i32 %a2) {
; CHECK-LABEL: cv_macsn_1:
; CHECK: seal5.cv.macsn
  %result = call i32 @llvm.riscv.xcorevmac.mac.macsn(i32 %a0, i32 %a1, i32 %a2, i32 1)
  ret i32 %result
}

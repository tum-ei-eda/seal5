; RUN: llc -O0 -mtriple=riscv32 -mattr=+m,+xopenasipbase -verify-machineinstrs < %s \
; RUN:   | FileCheck %s

declare i32 @llvm.riscv.openasip.base.maxu(i32, i32)

define i32 @umax(i32 %a, i32 %b) {
; CHECK-LABEL: umax:
; CHECK:       # %bb.0:
; CHECK-NEXT:    openasip_base_maxu a0, a0, a1
; CHECK-NEXT:    ret
  %1 = call i32 @llvm.riscv.openasip.base.maxu(i32 %a, i32 %b)
  ret i32 %1
}

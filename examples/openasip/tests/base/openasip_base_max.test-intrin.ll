; RUN: llc -O0 -mtriple=riscv32 -mattr=+m,+experimental-xopenasipbase -verify-machineinstrs < %s \
; RUN:   | FileCheck %s

declare i32 @llvm.riscv.xopenasipbase.openasip.base.max(i32, i32)

define i32 @smax(i32 %a, i32 %b) {
; CHECK-LABEL: smax:
; CHECK:       # %bb.0:
; CHECK-NEXT:    openasip_base_max a0, a0, a1
; CHECK-NEXT:    ret
  %1 = call i32 @llvm.riscv.xopenasipbase.openasip.base.max(i32 %a, i32 %b)
  ret i32 %1
}

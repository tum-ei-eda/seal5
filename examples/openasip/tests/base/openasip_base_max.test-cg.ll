; RUN: llc -O0 -mtriple=riscv32 -mattr=+m,+experimental-xopenasipbase -verify-machineinstrs -global-isel=1 < %s \
; RUN:   | FileCheck %s --check-prefixes=CHECK,CHECK-GISEL

declare i32 @llvm.smax.i32(i32, i32)

define i32 @smax(i32 %a, i32 %b) {
; CHECK-LABEL: smax:
; CHECK:       # %bb.0:
; CHECK-GISEL-NEXT:    openasip_base_max a0, a0, a1
; CHECK-NEXT:    ret
  %1 = call i32 @llvm.smax.i32(i32 %a, i32 %b)
  ret i32 %1
}

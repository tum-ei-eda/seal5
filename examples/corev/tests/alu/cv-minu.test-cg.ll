; RUN: llc -O0 -mtriple=riscv32 -mattr=+m,+xcorevalu -verify-machineinstrs -global-isel=1 -global-isel-abort=1 < %s \
; RUN:   | FileCheck %s

declare i32 @llvm.umin.i32(i32, i32)

define i32 @minu(i32 %a, i32 %b) {
; CHECK-LABEL: minu:
; CHECK: seal5.cv.minu
; CHECK: ret
  %1 = call i32 @llvm.umin.i32(i32 %a, i32 %b)
  ret i32 %1
}

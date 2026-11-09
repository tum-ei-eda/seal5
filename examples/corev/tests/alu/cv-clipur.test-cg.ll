; RUN: llc -O0 -mtriple=riscv32 -mattr=+m,+xcorevalu -verify-machineinstrs -global-isel=1 -global-isel-abort=1 < %s \
; RUN:   | FileCheck %s

declare i32 @llvm.umin.i32(i32, i32)
declare i32 @llvm.umax.i32(i32, i32)

define i32 @clipur(i32 %a, i32 %b) {
; CHECK-LABEL: clipur:
; CHECK: seal5.cv.clipur
; CHECK: ret
  %1 = call i32 @llvm.smax.i32(i32 %a, i32 0)
  %2 = call i32 @llvm.smin.i32(i32 %1, i32 %b)
  ret i32 %2
}

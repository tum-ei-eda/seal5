; RUN: llc -O0 -mtriple=riscv32 -mattr=+m,+xcorevalu -verify-machineinstrs -global-isel=1 -global-isel-abort=1 < %s \
; RUN:   | FileCheck %s

declare i32 @llvm.smin.i32(i32, i32)
declare i32 @llvm.smax.i32(i32, i32)

define i32 @clipr(i32 %a, i32 %b) {
; CHECK-LABEL: clipr:
; CHECK: seal5.cv.clipr
; CHECK: ret
  %1 = xor i32 %b, -1
  %2 = call i32 @llvm.smax.i32(i32 %a, i32 %1)
  %3 = call i32 @llvm.smin.i32(i32 %2, i32 %b)
  ret i32 %3
}

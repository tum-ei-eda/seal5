; RUN: llc -O0 -mtriple=riscv32 -mattr=+m,+xcorevalu -verify-machineinstrs -global-isel=1 -global-isel-abort=1 < %s \
; RUN:   | FileCheck %s

declare i32 @llvm.smin.i32(i32, i32)

define i32 @min(i32 %a, i32 %b) {
; CHECK-LABEL: min:
; CHECK: seal5.cv.min
; CHECK: ret
  %1 = call i32 @llvm.smin.i32(i32 %a, i32 %b)
  ret i32 %1
}

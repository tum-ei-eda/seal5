; RUN: llc -O0 -mtriple=riscv32 -mattr=+m,+xcorevalu -verify-machineinstrs -global-isel=1 -global-isel-abort=1 < %s \
; RUN:   | FileCheck %s

declare i32 @llvm.abs.i32(i32, i1)

define i32 @abs(i32 %a) {
; CHECK-LABEL: abs:
; CHECK: seal5.cv.abs
; CHECK: ret
  %1 = call i32 @llvm.abs.i32(i32 %a, i1 false)
  ret i32 %1
}

; RUN: llc -O0 -mtriple=riscv32 -mattr=+m,+xcorevalu -verify-machineinstrs -global-isel=1 -global-isel-abort=1 < %s \
; RUN:   | FileCheck %s

declare i32 @llvm.smax.i32(i32, i32)

define i32 @max(i32 %a, i32 %b) {
; CHECK-LABEL: max:
; CHECK: seal5.cv.max
; CHECK: ret
  %1 = call i32 @llvm.smax.i32(i32 %a, i32 %b)
  ret i32 %1
}

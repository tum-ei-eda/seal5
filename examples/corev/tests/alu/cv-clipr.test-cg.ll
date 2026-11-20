; RUN: llc -O0 -mtriple=riscv32 -mattr=+m,+xcorevalu -verify-machineinstrs -global-isel=0 -global-isel-abort=1 < %s | FileCheck %s
; RUN: llc -O3 -mtriple=riscv32 -mattr=+m,+xcorevalu -verify-machineinstrs -global-isel=0 -global-isel-abort=1 < %s | FileCheck %s
; RUN: llc -O0 -mtriple=riscv32 -mattr=+m,+xcorevalu -verify-machineinstrs -global-isel=1 -global-isel-abort=1 < %s | FileCheck %s
; RUN: llc -O3 -mtriple=riscv32 -mattr=+m,+xcorevalu -verify-machineinstrs -global-isel=1 -global-isel-abort=1 < %s | FileCheck %s

declare i32 @llvm.smin.i32(i32, i32)
declare i32 @llvm.smax.i32(i32, i32)

define i32 @clipr_lower_first(i32 %a, i32 %b) {
; CHECK-LABEL: clipr_lower_first:
; CHECK: seal5.cv.clipr a0, a0, a1{{$}}
; CHECK: ret
  %bound = and i32 %b, 2147483647
  %lower = xor i32 %bound, -1
  %lo = call i32 @llvm.smax.i32(i32 %a, i32 %lower)
  %result = call i32 @llvm.smin.i32(i32 %lo, i32 %bound)
  ret i32 %result
}

define i32 @clipr_upper_first(i32 %a, i32 %b) {
; CHECK-LABEL: clipr_upper_first:
; CHECK: seal5.cv.clipr a0, a0, a1{{$}}
; CHECK: ret
  %bound = and i32 %b, 2147483647
  %lower = xor i32 %bound, -1
  %hi = call i32 @llvm.smin.i32(i32 %a, i32 %bound)
  %result = call i32 @llvm.smax.i32(i32 %hi, i32 %lower)
  ret i32 %result
}

define i32 @clipr_unmasked(i32 %a, i32 %b) {
; CHECK-LABEL: clipr_unmasked:
; CHECK-NOT: seal5.cv.clip
; CHECK: ret
  %lower = xor i32 %b, -1
  %lo = call i32 @llvm.smax.i32(i32 %a, i32 %lower)
  %hi = call i32 @llvm.smin.i32(i32 %lo, i32 %b)
  ret i32 %hi
}

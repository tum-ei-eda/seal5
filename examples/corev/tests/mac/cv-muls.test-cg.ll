; RUN: llc -O0 -mtriple=riscv32 -mattr=+m,+xcorevmac -verify-machineinstrs -global-isel=0 < %s | FileCheck %s
; RUN: llc -O3 -mtriple=riscv32 -mattr=+m,+xcorevmac -verify-machineinstrs -global-isel=0 < %s | FileCheck %s
; RUN: llc -O0 -mtriple=riscv32 -mattr=+m,+xcorevmac -verify-machineinstrs -global-isel=1 -global-isel-abort=1 < %s | FileCheck %s
; RUN: llc -O3 -mtriple=riscv32 -mattr=+m,+xcorevmac -verify-machineinstrs -global-isel=1 -global-isel-abort=1 < %s | FileCheck %s

define i32 @muls(i32 %a, i32 %b) {
; CHECK-LABEL: muls:
; CHECK: seal5.cv.mulsn {{[^,]+}}, {{[^,]+}}, {{[^,]+}}, 0
; CHECK: ret
  %1 = shl i32 %a, 16
  %2 = ashr i32 %1, 16
  %3 = shl i32 %b, 16
  %4 = ashr i32 %3, 16
  %5 = mul i32 %2, %4
  ret i32 %5
}

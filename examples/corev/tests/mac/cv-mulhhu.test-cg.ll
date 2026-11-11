; RUN: llc -O0 -mtriple=riscv32 -mattr=+m,+xcorevmac -verify-machineinstrs -global-isel=0 < %s | FileCheck %s
; RUN: llc -O3 -mtriple=riscv32 -mattr=+m,+xcorevmac -verify-machineinstrs -global-isel=0 < %s | FileCheck %s
; RUN: llc -O0 -mtriple=riscv32 -mattr=+m,+xcorevmac -verify-machineinstrs -global-isel=1 -global-isel-abort=1 < %s | FileCheck %s
; RUN: llc -O3 -mtriple=riscv32 -mattr=+m,+xcorevmac -verify-machineinstrs -global-isel=1 -global-isel-abort=1 < %s | FileCheck %s

define i32 @mulhhu(i32 %a, i32 %b) {
; CHECK-LABEL: mulhhu:
; CHECK: seal5.cv.mulhhun {{[^,]+}}, {{[^,]+}}, {{[^,]+}}, 0
; CHECK: ret
  %1 = lshr i32 %a, 16
  %2 = lshr i32 %b, 16
  %3 = mul i32 %1, %2
  ret i32 %3
}

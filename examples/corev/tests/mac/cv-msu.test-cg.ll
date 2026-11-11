; RUN: llc -O3 -mtriple=riscv32 -mattr=+m,+xcorevmac -verify-machineinstrs -global-isel=1 -global-isel-abort=1 < %s \
; RUN:   | FileCheck %s

define i32 @msu(i32 %a, i32 %b, i32 %c) {
; CHECK-LABEL: msu:
; CHECK: seal5.cv.msu
; CHECK: ret
  %1 = mul i32 %a, %b
  %2 = sub i32 %c, %1
  ret i32 %2
}

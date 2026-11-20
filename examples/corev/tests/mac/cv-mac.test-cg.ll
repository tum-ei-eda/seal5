; RUN: llc -O3 -mtriple=riscv32 -mattr=+m,+xcorevmac -verify-machineinstrs -global-isel=1 -global-isel-abort=1 < %s \
; RUN:   | FileCheck %s

define i32 @mac(i32 %a, i32 %b, i32 %c) {
; CHECK-LABEL: mac:
; CHECK: seal5.cv.mac
; CHECK: ret
  %1 = mul i32 %a, %b
  %2 = add i32 %1, %c
  ret i32 %2
}

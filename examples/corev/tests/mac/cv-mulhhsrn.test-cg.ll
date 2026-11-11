; RUN: llc -O0 -mtriple=riscv32 -mattr=+m,+xcorevmac -verify-machineinstrs -global-isel=1 -global-isel-abort=1 < %s \
; RUN:   | FileCheck %s

define i32 @mulhhsRN(i32 %a, i32 %b) {
; CHECK-LABEL: mulhhsRN:
; CHECK: seal5.cv.mulhhsrn
; CHECK: ret
  %1 = ashr i32 %a, 16
  %2 = ashr i32 %b, 16
  %3 = mul i32 %1, %2
  %4 = add i32 %3, 16
  %5 = ashr i32 %4, 5
  ret i32 %5
}

; RUN: llc -O0 -mtriple=riscv32 -mattr=+m,+xcorevmac -verify-machineinstrs -global-isel=1 -global-isel-abort=1 < %s \
; RUN:   | FileCheck %s

define i32 @mulhhsN(i32 %a, i32 %b) {
; CHECK-LABEL: mulhhsN:
; CHECK: seal5.cv.mulhhsn
; CHECK: ret
  %1 = ashr i32 %a, 16
  %2 = ashr i32 %b, 16
  %3 = mul i32 %1, %2
  %4 = ashr i32 %3, 5
  ret i32 %4
}

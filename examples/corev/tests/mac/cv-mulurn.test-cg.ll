; RUN: llc -O0 -mtriple=riscv32 -mattr=+m,+xcorevmac -verify-machineinstrs -global-isel=1 -global-isel-abort=1 < %s \
; RUN:   | FileCheck %s

define i32 @muluRN(i32 %a, i32 %b) {
; CHECK-LABEL: muluRN:
; CHECK: seal5.cv.mulurn
; CHECK: ret
  %1 = and i32 %a, 65535
  %2 = and i32 %b, 65535
  %3 = mul i32 %1, %2
  %4 = add i32 %3, 16
  %5 = lshr i32 %4, 5
  ret i32 %5
}

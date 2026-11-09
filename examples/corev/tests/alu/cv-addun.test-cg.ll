; RUN: llc -O0 -mtriple=riscv32 -mattr=+m,+xcorevalu -verify-machineinstrs -global-isel=1 -global-isel-abort=1 < %s \
; RUN:   | FileCheck %s

define i32 @adduN(i32 %a, i32 %b) {
; CHECK-LABEL: adduN:
; CHECK: seal5.cv.adduN
; CHECK: ret
  %1 = add i32 %a, %b
  %2 = lshr i32 %1, 5
  ret i32 %2
}

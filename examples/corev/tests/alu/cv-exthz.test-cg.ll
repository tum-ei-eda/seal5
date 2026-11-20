; RUN: llc -O0 -mtriple=riscv32 -mattr=+m,+xcorevalu -verify-machineinstrs -global-isel=1 -global-isel-abort=1 < %s \
; RUN:   | FileCheck %s

define i32 @exthz(i16 %a) {
; CHECK-LABEL: exthz:
; CHECK: seal5.cv.exthz
; CHECK: ret
  %1 = zext i16 %a to i32
  ret i32 %1
}

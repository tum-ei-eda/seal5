; RUN: llc -O3 -mtriple=riscv32 -mattr=+xnormalize32 -verify-machineinstrs -global-isel=1 < %s | FileCheck %s

define i32 @extract8(i32 %value) {
; CHECK-LABEL: extract8:
; CHECK: xnormalize32.extract a0, a0, 8
  %shift = lshr i32 %value, 8
  %result = and i32 %shift, 255
  ret i32 %result
}

define i32 @extract4(i32 %value) {
; CHECK-LABEL: extract4:
; CHECK: xnormalize32.extract4 a0, a0, 8
  %shift = lshr i32 %value, 8
  %result = and i32 %shift, 15
  ret i32 %result
}

define i32 @extract8_unaligned(i32 %value) {
; CHECK-LABEL: extract8_unaligned:
; CHECK: xnormalize32.extract a0, a0, 3
  %shift = lshr i32 %value, 3
  %result = and i32 %shift, 255
  ret i32 %result
}

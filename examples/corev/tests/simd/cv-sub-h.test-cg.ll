; RUN: llc -mtriple=riscv32 -mattr=+m,+xcorevsimd -verify-machineinstrs %s -o - | FileCheck %s
; RUN: llc -mtriple=riscv32 -mattr=+m,+xcorevsimd -global-isel=1 -global-isel-abort=1 -verify-machineinstrs %s -o - | FileCheck %s

define i32 @packed_sub_h(i32 %a_bits, i32 %b_bits) {
; CHECK-LABEL: packed_sub_h:
; CHECK: seal5.cv.sub.h
  %a = bitcast i32 %a_bits to <2 x i16>
  %b = bitcast i32 %b_bits to <2 x i16>
  %r = sub <2 x i16> %a, %b
  %result = bitcast <2 x i16> %r to i32
  ret i32 %result
}

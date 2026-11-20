; RUN: llc -mtriple=riscv32 -mattr=+m,+xcorevsimd -verify-machineinstrs %s -o - | FileCheck %s
; RUN: llc -mtriple=riscv32 -mattr=+m,+xcorevsimd -global-isel=1 -global-isel-abort=1 -verify-machineinstrs %s -o - | FileCheck %s

define i32 @packed_sub_b(i32 %a_bits, i32 %b_bits) {
; CHECK-LABEL: packed_sub_b:
; CHECK: seal5.cv.sub.b
  %a = bitcast i32 %a_bits to <4 x i8>
  %b = bitcast i32 %b_bits to <4 x i8>
  %r = sub <4 x i8> %a, %b
  %result = bitcast <4 x i8> %r to i32
  ret i32 %result
}

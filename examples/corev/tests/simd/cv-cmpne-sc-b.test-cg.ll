; Scalar broadcast compares use only the low lane of rs2; each result lane is all ones or zero.
; RUN: llc -mtriple=riscv32 -mattr=+m,+xcorevsimd -O0 -verify-machineinstrs %s -o - | FileCheck %s
; RUN: llc -mtriple=riscv32 -mattr=+m,+xcorevsimd -O3 -verify-machineinstrs %s -o - | FileCheck --check-prefix=CHECK %s
; RUN: llc -mtriple=riscv32 -mattr=+m,+xcorevsimd -O0 -global-isel=1 -global-isel-abort=1 -verify-machineinstrs %s -o - | FileCheck %s
; RUN: llc -mtriple=riscv32 -mattr=+m,+xcorevsimd -O3 -global-isel=1 -global-isel-abort=1 -verify-machineinstrs %s -o - | FileCheck --check-prefix=CHECK %s

define i32 @packed_cmpne_sc_b(i32 %a, i32 %b) {
; CHECK-LABEL: packed_cmpne_sc_b:
; CHECK: seal5.cv.cmpne.sc.b
  %av = bitcast i32 %a to <4 x i8>
  %bt = trunc i32 %b to i8
  %b0 = insertelement <4 x i8> poison, i8 %bt, i32 0
  %bv = shufflevector <4 x i8> %b0, <4 x i8> poison, <4 x i32> zeroinitializer
  %c = icmp ne <4 x i8> %av, %bv
  %r = sext <4 x i1> %c to <4 x i8>
  %ret = bitcast <4 x i8> %r to i32
  ret i32 %ret
}

define i32 @packed_cmpne_sc_b_swapped(i32 %a, i32 %b) {
; CHECK-LABEL: packed_cmpne_sc_b_swapped:
; CHECK: seal5.cv.cmpne.sc.b
  %av = bitcast i32 %a to <4 x i8>
  %bt = trunc i32 %b to i8
  %b0 = insertelement <4 x i8> poison, i8 %bt, i32 0
  %bv = shufflevector <4 x i8> %b0, <4 x i8> poison, <4 x i32> zeroinitializer
  %c = icmp ne <4 x i8> %bv, %av
  %r = sext <4 x i1> %c to <4 x i8>
  %ret = bitcast <4 x i8> %r to i32
  ret i32 %ret
}

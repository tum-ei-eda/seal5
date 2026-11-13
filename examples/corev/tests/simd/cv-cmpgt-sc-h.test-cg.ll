; Scalar broadcast compares use only the low lane of rs2; each result lane is all ones or zero.
; RUN: llc -mtriple=riscv32 -mattr=+m,+xcorevsimd -O0 -verify-machineinstrs %s -o - | FileCheck %s
; RUN: llc -mtriple=riscv32 -mattr=+m,+xcorevsimd -O3 -verify-machineinstrs %s -o - | FileCheck --check-prefix=CHECK %s
; RUN: llc -mtriple=riscv32 -mattr=+m,+xcorevsimd -O0 -global-isel=1 -global-isel-abort=1 -verify-machineinstrs %s -o - | FileCheck %s
; RUN: llc -mtriple=riscv32 -mattr=+m,+xcorevsimd -O3 -global-isel=1 -global-isel-abort=1 -verify-machineinstrs %s -o - | FileCheck --check-prefix=CHECK %s

define i32 @packed_cmpgt_sc_h(i32 %a, i32 %b) {
; CHECK-LABEL: packed_cmpgt_sc_h:
; CHECK: seal5.cv.cmpgt.sc.h
  %av = bitcast i32 %a to <2 x i16>
  %bt = trunc i32 %b to i16
  %b0 = insertelement <2 x i16> poison, i16 %bt, i32 0
  %bv = shufflevector <2 x i16> %b0, <2 x i16> poison, <2 x i32> zeroinitializer
  %c = icmp sgt <2 x i16> %av, %bv
  %r = sext <2 x i1> %c to <2 x i16>
  %ret = bitcast <2 x i16> %r to i32
  ret i32 %ret
}

define i32 @packed_cmpgt_sc_h_swapped(i32 %a, i32 %b) {
; CHECK-LABEL: packed_cmpgt_sc_h_swapped:
; CHECK: seal5.cv.cmpgt.sc.h
  %av = bitcast i32 %a to <2 x i16>
  %bt = trunc i32 %b to i16
  %b0 = insertelement <2 x i16> poison, i16 %bt, i32 0
  %bv = shufflevector <2 x i16> %b0, <2 x i16> poison, <2 x i32> zeroinitializer
  %c = icmp slt <2 x i16> %bv, %av
  %r = sext <2 x i1> %c to <2 x i16>
  %ret = bitcast <2 x i16> %r to i32
  ret i32 %ret
}

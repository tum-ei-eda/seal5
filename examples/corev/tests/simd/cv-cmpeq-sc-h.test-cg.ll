; Scalar broadcast compares use only the low lane of rs2; each result lane is all ones or zero.
; RUN: llc -mtriple=riscv32 -mattr=+m,+xcorevsimd -O0 -verify-machineinstrs %s -o - | FileCheck %s
; RUN: llc -mtriple=riscv32 -mattr=+m,+xcorevsimd -O3 -verify-machineinstrs %s -o - | FileCheck --check-prefix=CHECK %s
; RUN: llc -mtriple=riscv32 -mattr=+m,+xcorevsimd -O0 -global-isel=1 -global-isel-abort=1 -verify-machineinstrs %s -o - | FileCheck %s
; RUN: llc -mtriple=riscv32 -mattr=+m,+xcorevsimd -O3 -global-isel=1 -global-isel-abort=1 -verify-machineinstrs %s -o - | FileCheck --check-prefix=CHECK %s
; RUN: llc -mtriple=riscv32 -mattr=+m,+xcorevsimd,-gpr32v-cmp -verify-machineinstrs %s -o - | FileCheck --check-prefix=FALLBACK %s
; RUN: llc -mtriple=riscv32 -mattr=+m,+xcorevsimd,-gpr32v-cmp -global-isel=1 -global-isel-abort=1 -verify-machineinstrs %s -o - | FileCheck --check-prefix=FALLBACK %s
; FALLBACK: .file
; FALLBACK-NOT: seal5.cv.cmp
; RUN: opt -mtriple=riscv32 -mattr=+gpr32v-cmp -passes='print<cost-model>' -disable-output %s 2>&1 | FileCheck --check-prefix=COST %s
; COST-LABEL: for function 'packed_cmpeq_sc_h':
; COST: estimated cost of 0 for instruction: {{%.*}} = bitcast i32
; COST: estimated cost of 0 for instruction: {{%.*}} = insertelement
; COST: estimated cost of 0 for instruction: {{%.*}} = shufflevector
; COST: estimated cost of 1 for instruction: {{%.*}} = icmp eq <2 x i16>
; COST: estimated cost of 0 for instruction: {{%.*}} = sext <2 x i1>

define i32 @packed_cmpeq_sc_h(i32 %a, i32 %b) {
; CHECK-LABEL: packed_cmpeq_sc_h:
; CHECK: seal5.cv.cmpeq.sc.h
  %av = bitcast i32 %a to <2 x i16>
  %bt = trunc i32 %b to i16
  %b0 = insertelement <2 x i16> poison, i16 %bt, i32 0
  %bv = shufflevector <2 x i16> %b0, <2 x i16> poison, <2 x i32> zeroinitializer
  %c = icmp eq <2 x i16> %av, %bv
  %r = sext <2 x i1> %c to <2 x i16>
  %ret = bitcast <2 x i16> %r to i32
  ret i32 %ret
}

define i32 @packed_cmpeq_sc_h_swapped(i32 %a, i32 %b) {
; CHECK-LABEL: packed_cmpeq_sc_h_swapped:
; CHECK: seal5.cv.cmpeq.sc.h
  %av = bitcast i32 %a to <2 x i16>
  %bt = trunc i32 %b to i16
  %b0 = insertelement <2 x i16> poison, i16 %bt, i32 0
  %bv = shufflevector <2 x i16> %b0, <2 x i16> poison, <2 x i32> zeroinitializer
  %c = icmp eq <2 x i16> %bv, %av
  %r = sext <2 x i1> %c to <2 x i16>
  %ret = bitcast <2 x i16> %r to i32
  ret i32 %ret
}


; An unfused broadcast must also have a selector fallback.
define i32 @standalone_splat_16(i32 %b) {
; CHECK-LABEL: standalone_splat_16:
; CHECK: ret
  %bt = trunc i32 %b to i16
  %b0 = insertelement <2 x i16> poison, i16 %bt, i32 0
  %bv = shufflevector <2 x i16> %b0, <2 x i16> poison, <2 x i32> zeroinitializer
  %ret = bitcast <2 x i16> %bv to i32
  ret i32 %ret
}

; COST-LABEL: for function 'standalone_splat_16':
; COST: estimated cost of 3 for instruction: {{%.*}} = shufflevector
; COST: estimated cost of 0 for instruction: {{%.*}} = bitcast <2 x i16>

; COST-LABEL: for function 'shared_splat_16':
; COST: estimated cost of 3 for instruction: {{%.*}} = shufflevector
define i32 @shared_splat_16(i32 %a, i32 %b, ptr %out) {
  %av = bitcast i32 %a to <2 x i16>
  %bt = trunc i32 %b to i16
  %b0 = insertelement <2 x i16> poison, i16 %bt, i32 0
  %bv = shufflevector <2 x i16> %b0, <2 x i16> poison, <2 x i32> zeroinitializer
  store <2 x i16> %bv, ptr %out, align 4
  %c = icmp eq <2 x i16> %av, %bv
  %r = sext <2 x i1> %c to <2 x i16>
  %ret = bitcast <2 x i16> %r to i32
  ret i32 %ret
}

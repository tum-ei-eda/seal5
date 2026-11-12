; RUN: llc -O0 -mtriple=riscv32 -mattr=+m,+xcorevmac -verify-machineinstrs -global-isel=0 -global-isel-abort=1 < %s | FileCheck %s
; RUN: llc -O3 -mtriple=riscv32 -mattr=+m,+xcorevmac -verify-machineinstrs -global-isel=0 -global-isel-abort=1 < %s | FileCheck %s
; RUN: llc -O0 -mtriple=riscv32 -mattr=+m,+xcorevmac -verify-machineinstrs -global-isel=1 -global-isel-abort=1 < %s | FileCheck %s
; RUN: llc -O3 -mtriple=riscv32 -mattr=+m,+xcorevmac -verify-machineinstrs -global-isel=1 -global-isel-abort=1 < %s | FileCheck %s

define i32 @mulsrn_0(i32 %a, i32 %b) {
; CHECK-LABEL: mulsrn_0:
; CHECK: seal5.cv.muls{{r?}}n {{.*}}, 0{{$}}
; CHECK: ret
  %ashift = shl i32 %a, 16
  %ahalf = ashr i32 %ashift, 16
  %bshift = shl i32 %b, 16
  %bhalf = ashr i32 %bshift, 16
  %product = mul i32 %ahalf, %bhalf
  ret i32 %product
}

define i32 @mulsrn_1(i32 %a, i32 %b) {
; CHECK-LABEL: mulsrn_1:
; CHECK: seal5.cv.mulsrn {{.*}}, 1{{$}}
; CHECK: ret
  %ashift = shl i32 %a, 16
  %ahalf = ashr i32 %ashift, 16
  %bshift = shl i32 %b, 16
  %bhalf = ashr i32 %bshift, 16
  %product = mul i32 %ahalf, %bhalf
  %rounded = add i32 %product, 1
  %result = ashr i32 %rounded, 1
  ret i32 %result
}

define i32 @mulsrn_2(i32 %a, i32 %b) {
; CHECK-LABEL: mulsrn_2:
; CHECK: seal5.cv.mulsrn {{.*}}, 2{{$}}
; CHECK: ret
  %ashift = shl i32 %a, 16
  %ahalf = ashr i32 %ashift, 16
  %bshift = shl i32 %b, 16
  %bhalf = ashr i32 %bshift, 16
  %product = mul i32 %ahalf, %bhalf
  %rounded = add i32 %product, 2
  %result = ashr i32 %rounded, 2
  ret i32 %result
}

define i32 @mulsrn_3(i32 %a, i32 %b) {
; CHECK-LABEL: mulsrn_3:
; CHECK: seal5.cv.mulsrn {{.*}}, 3{{$}}
; CHECK: ret
  %ashift = shl i32 %a, 16
  %ahalf = ashr i32 %ashift, 16
  %bshift = shl i32 %b, 16
  %bhalf = ashr i32 %bshift, 16
  %product = mul i32 %ahalf, %bhalf
  %rounded = add i32 %product, 4
  %result = ashr i32 %rounded, 3
  ret i32 %result
}

define i32 @mulsrn_4(i32 %a, i32 %b) {
; CHECK-LABEL: mulsrn_4:
; CHECK: seal5.cv.mulsrn {{.*}}, 4{{$}}
; CHECK: ret
  %ashift = shl i32 %a, 16
  %ahalf = ashr i32 %ashift, 16
  %bshift = shl i32 %b, 16
  %bhalf = ashr i32 %bshift, 16
  %product = mul i32 %ahalf, %bhalf
  %rounded = add i32 %product, 8
  %result = ashr i32 %rounded, 4
  ret i32 %result
}

define i32 @mulsrn_5(i32 %a, i32 %b) {
; CHECK-LABEL: mulsrn_5:
; CHECK: seal5.cv.mulsrn {{.*}}, 5{{$}}
; CHECK: ret
  %ashift = shl i32 %a, 16
  %ahalf = ashr i32 %ashift, 16
  %bshift = shl i32 %b, 16
  %bhalf = ashr i32 %bshift, 16
  %product = mul i32 %ahalf, %bhalf
  %rounded = add i32 %product, 16
  %result = ashr i32 %rounded, 5
  ret i32 %result
}

define i32 @mulsrn_6(i32 %a, i32 %b) {
; CHECK-LABEL: mulsrn_6:
; CHECK: seal5.cv.mulsrn {{.*}}, 6{{$}}
; CHECK: ret
  %ashift = shl i32 %a, 16
  %ahalf = ashr i32 %ashift, 16
  %bshift = shl i32 %b, 16
  %bhalf = ashr i32 %bshift, 16
  %product = mul i32 %ahalf, %bhalf
  %rounded = add i32 %product, 32
  %result = ashr i32 %rounded, 6
  ret i32 %result
}

define i32 @mulsrn_7(i32 %a, i32 %b) {
; CHECK-LABEL: mulsrn_7:
; CHECK: seal5.cv.mulsrn {{.*}}, 7{{$}}
; CHECK: ret
  %ashift = shl i32 %a, 16
  %ahalf = ashr i32 %ashift, 16
  %bshift = shl i32 %b, 16
  %bhalf = ashr i32 %bshift, 16
  %product = mul i32 %ahalf, %bhalf
  %rounded = add i32 %product, 64
  %result = ashr i32 %rounded, 7
  ret i32 %result
}

define i32 @mulsrn_8(i32 %a, i32 %b) {
; CHECK-LABEL: mulsrn_8:
; CHECK: seal5.cv.mulsrn {{.*}}, 8{{$}}
; CHECK: ret
  %ashift = shl i32 %a, 16
  %ahalf = ashr i32 %ashift, 16
  %bshift = shl i32 %b, 16
  %bhalf = ashr i32 %bshift, 16
  %product = mul i32 %ahalf, %bhalf
  %rounded = add i32 %product, 128
  %result = ashr i32 %rounded, 8
  ret i32 %result
}

define i32 @mulsrn_9(i32 %a, i32 %b) {
; CHECK-LABEL: mulsrn_9:
; CHECK: seal5.cv.mulsrn {{.*}}, 9{{$}}
; CHECK: ret
  %ashift = shl i32 %a, 16
  %ahalf = ashr i32 %ashift, 16
  %bshift = shl i32 %b, 16
  %bhalf = ashr i32 %bshift, 16
  %product = mul i32 %ahalf, %bhalf
  %rounded = add i32 %product, 256
  %result = ashr i32 %rounded, 9
  ret i32 %result
}

define i32 @mulsrn_10(i32 %a, i32 %b) {
; CHECK-LABEL: mulsrn_10:
; CHECK: seal5.cv.mulsrn {{.*}}, 10{{$}}
; CHECK: ret
  %ashift = shl i32 %a, 16
  %ahalf = ashr i32 %ashift, 16
  %bshift = shl i32 %b, 16
  %bhalf = ashr i32 %bshift, 16
  %product = mul i32 %ahalf, %bhalf
  %rounded = add i32 %product, 512
  %result = ashr i32 %rounded, 10
  ret i32 %result
}

define i32 @mulsrn_11(i32 %a, i32 %b) {
; CHECK-LABEL: mulsrn_11:
; CHECK: seal5.cv.mulsrn {{.*}}, 11{{$}}
; CHECK: ret
  %ashift = shl i32 %a, 16
  %ahalf = ashr i32 %ashift, 16
  %bshift = shl i32 %b, 16
  %bhalf = ashr i32 %bshift, 16
  %product = mul i32 %ahalf, %bhalf
  %rounded = add i32 %product, 1024
  %result = ashr i32 %rounded, 11
  ret i32 %result
}

define i32 @mulsrn_12(i32 %a, i32 %b) {
; CHECK-LABEL: mulsrn_12:
; CHECK: seal5.cv.mulsrn {{.*}}, 12{{$}}
; CHECK: ret
  %ashift = shl i32 %a, 16
  %ahalf = ashr i32 %ashift, 16
  %bshift = shl i32 %b, 16
  %bhalf = ashr i32 %bshift, 16
  %product = mul i32 %ahalf, %bhalf
  %rounded = add i32 %product, 2048
  %result = ashr i32 %rounded, 12
  ret i32 %result
}

define i32 @mulsrn_13(i32 %a, i32 %b) {
; CHECK-LABEL: mulsrn_13:
; CHECK: seal5.cv.mulsrn {{.*}}, 13{{$}}
; CHECK: ret
  %ashift = shl i32 %a, 16
  %ahalf = ashr i32 %ashift, 16
  %bshift = shl i32 %b, 16
  %bhalf = ashr i32 %bshift, 16
  %product = mul i32 %ahalf, %bhalf
  %rounded = add i32 %product, 4096
  %result = ashr i32 %rounded, 13
  ret i32 %result
}

define i32 @mulsrn_14(i32 %a, i32 %b) {
; CHECK-LABEL: mulsrn_14:
; CHECK: seal5.cv.mulsrn {{.*}}, 14{{$}}
; CHECK: ret
  %ashift = shl i32 %a, 16
  %ahalf = ashr i32 %ashift, 16
  %bshift = shl i32 %b, 16
  %bhalf = ashr i32 %bshift, 16
  %product = mul i32 %ahalf, %bhalf
  %rounded = add i32 %product, 8192
  %result = ashr i32 %rounded, 14
  ret i32 %result
}

define i32 @mulsrn_15(i32 %a, i32 %b) {
; CHECK-LABEL: mulsrn_15:
; CHECK: seal5.cv.mulsrn {{.*}}, 15{{$}}
; CHECK: ret
  %ashift = shl i32 %a, 16
  %ahalf = ashr i32 %ashift, 16
  %bshift = shl i32 %b, 16
  %bhalf = ashr i32 %bshift, 16
  %product = mul i32 %ahalf, %bhalf
  %rounded = add i32 %product, 16384
  %result = ashr i32 %rounded, 15
  ret i32 %result
}

define i32 @mulsrn_16(i32 %a, i32 %b) {
; CHECK-LABEL: mulsrn_16:
; CHECK: seal5.cv.mulsrn {{.*}}, 16{{$}}
; CHECK: ret
  %ashift = shl i32 %a, 16
  %ahalf = ashr i32 %ashift, 16
  %bshift = shl i32 %b, 16
  %bhalf = ashr i32 %bshift, 16
  %product = mul i32 %ahalf, %bhalf
  %rounded = add i32 %product, 32768
  %result = ashr i32 %rounded, 16
  ret i32 %result
}

define i32 @mulsrn_17(i32 %a, i32 %b) {
; CHECK-LABEL: mulsrn_17:
; CHECK: seal5.cv.mulsrn {{.*}}, 17{{$}}
; CHECK: ret
  %ashift = shl i32 %a, 16
  %ahalf = ashr i32 %ashift, 16
  %bshift = shl i32 %b, 16
  %bhalf = ashr i32 %bshift, 16
  %product = mul i32 %ahalf, %bhalf
  %rounded = add i32 %product, 65536
  %result = ashr i32 %rounded, 17
  ret i32 %result
}

define i32 @mulsrn_18(i32 %a, i32 %b) {
; CHECK-LABEL: mulsrn_18:
; CHECK: seal5.cv.mulsrn {{.*}}, 18{{$}}
; CHECK: ret
  %ashift = shl i32 %a, 16
  %ahalf = ashr i32 %ashift, 16
  %bshift = shl i32 %b, 16
  %bhalf = ashr i32 %bshift, 16
  %product = mul i32 %ahalf, %bhalf
  %rounded = add i32 %product, 131072
  %result = ashr i32 %rounded, 18
  ret i32 %result
}

define i32 @mulsrn_19(i32 %a, i32 %b) {
; CHECK-LABEL: mulsrn_19:
; CHECK: seal5.cv.mulsrn {{.*}}, 19{{$}}
; CHECK: ret
  %ashift = shl i32 %a, 16
  %ahalf = ashr i32 %ashift, 16
  %bshift = shl i32 %b, 16
  %bhalf = ashr i32 %bshift, 16
  %product = mul i32 %ahalf, %bhalf
  %rounded = add i32 %product, 262144
  %result = ashr i32 %rounded, 19
  ret i32 %result
}

define i32 @mulsrn_20(i32 %a, i32 %b) {
; CHECK-LABEL: mulsrn_20:
; CHECK: seal5.cv.mulsrn {{.*}}, 20{{$}}
; CHECK: ret
  %ashift = shl i32 %a, 16
  %ahalf = ashr i32 %ashift, 16
  %bshift = shl i32 %b, 16
  %bhalf = ashr i32 %bshift, 16
  %product = mul i32 %ahalf, %bhalf
  %rounded = add i32 %product, 524288
  %result = ashr i32 %rounded, 20
  ret i32 %result
}

define i32 @mulsrn_21(i32 %a, i32 %b) {
; CHECK-LABEL: mulsrn_21:
; CHECK: seal5.cv.mulsrn {{.*}}, 21{{$}}
; CHECK: ret
  %ashift = shl i32 %a, 16
  %ahalf = ashr i32 %ashift, 16
  %bshift = shl i32 %b, 16
  %bhalf = ashr i32 %bshift, 16
  %product = mul i32 %ahalf, %bhalf
  %rounded = add i32 %product, 1048576
  %result = ashr i32 %rounded, 21
  ret i32 %result
}

define i32 @mulsrn_22(i32 %a, i32 %b) {
; CHECK-LABEL: mulsrn_22:
; CHECK: seal5.cv.mulsrn {{.*}}, 22{{$}}
; CHECK: ret
  %ashift = shl i32 %a, 16
  %ahalf = ashr i32 %ashift, 16
  %bshift = shl i32 %b, 16
  %bhalf = ashr i32 %bshift, 16
  %product = mul i32 %ahalf, %bhalf
  %rounded = add i32 %product, 2097152
  %result = ashr i32 %rounded, 22
  ret i32 %result
}

define i32 @mulsrn_23(i32 %a, i32 %b) {
; CHECK-LABEL: mulsrn_23:
; CHECK: seal5.cv.mulsrn {{.*}}, 23{{$}}
; CHECK: ret
  %ashift = shl i32 %a, 16
  %ahalf = ashr i32 %ashift, 16
  %bshift = shl i32 %b, 16
  %bhalf = ashr i32 %bshift, 16
  %product = mul i32 %ahalf, %bhalf
  %rounded = add i32 %product, 4194304
  %result = ashr i32 %rounded, 23
  ret i32 %result
}

define i32 @mulsrn_24(i32 %a, i32 %b) {
; CHECK-LABEL: mulsrn_24:
; CHECK: seal5.cv.mulsrn {{.*}}, 24{{$}}
; CHECK: ret
  %ashift = shl i32 %a, 16
  %ahalf = ashr i32 %ashift, 16
  %bshift = shl i32 %b, 16
  %bhalf = ashr i32 %bshift, 16
  %product = mul i32 %ahalf, %bhalf
  %rounded = add i32 %product, 8388608
  %result = ashr i32 %rounded, 24
  ret i32 %result
}

define i32 @mulsrn_25(i32 %a, i32 %b) {
; CHECK-LABEL: mulsrn_25:
; CHECK: seal5.cv.mulsrn {{.*}}, 25{{$}}
; CHECK: ret
  %ashift = shl i32 %a, 16
  %ahalf = ashr i32 %ashift, 16
  %bshift = shl i32 %b, 16
  %bhalf = ashr i32 %bshift, 16
  %product = mul i32 %ahalf, %bhalf
  %rounded = add i32 %product, 16777216
  %result = ashr i32 %rounded, 25
  ret i32 %result
}

define i32 @mulsrn_26(i32 %a, i32 %b) {
; CHECK-LABEL: mulsrn_26:
; CHECK: seal5.cv.mulsrn {{.*}}, 26{{$}}
; CHECK: ret
  %ashift = shl i32 %a, 16
  %ahalf = ashr i32 %ashift, 16
  %bshift = shl i32 %b, 16
  %bhalf = ashr i32 %bshift, 16
  %product = mul i32 %ahalf, %bhalf
  %rounded = add i32 %product, 33554432
  %result = ashr i32 %rounded, 26
  ret i32 %result
}

define i32 @mulsrn_27(i32 %a, i32 %b) {
; CHECK-LABEL: mulsrn_27:
; CHECK: seal5.cv.mulsrn {{.*}}, 27{{$}}
; CHECK: ret
  %ashift = shl i32 %a, 16
  %ahalf = ashr i32 %ashift, 16
  %bshift = shl i32 %b, 16
  %bhalf = ashr i32 %bshift, 16
  %product = mul i32 %ahalf, %bhalf
  %rounded = add i32 %product, 67108864
  %result = ashr i32 %rounded, 27
  ret i32 %result
}

define i32 @mulsrn_28(i32 %a, i32 %b) {
; CHECK-LABEL: mulsrn_28:
; CHECK: seal5.cv.mulsrn {{.*}}, 28{{$}}
; CHECK: ret
  %ashift = shl i32 %a, 16
  %ahalf = ashr i32 %ashift, 16
  %bshift = shl i32 %b, 16
  %bhalf = ashr i32 %bshift, 16
  %product = mul i32 %ahalf, %bhalf
  %rounded = add i32 %product, 134217728
  %result = ashr i32 %rounded, 28
  ret i32 %result
}

define i32 @mulsrn_29(i32 %a, i32 %b) {
; CHECK-LABEL: mulsrn_29:
; CHECK: seal5.cv.mulsrn {{.*}}, 29{{$}}
; CHECK: ret
  %ashift = shl i32 %a, 16
  %ahalf = ashr i32 %ashift, 16
  %bshift = shl i32 %b, 16
  %bhalf = ashr i32 %bshift, 16
  %product = mul i32 %ahalf, %bhalf
  %rounded = add i32 %product, 268435456
  %result = ashr i32 %rounded, 29
  ret i32 %result
}

define i32 @mulsrn_30(i32 %a, i32 %b) {
; CHECK-LABEL: mulsrn_30:
; CHECK: seal5.cv.mulsrn {{.*}}, 30{{$}}
; CHECK: ret
  %ashift = shl i32 %a, 16
  %ahalf = ashr i32 %ashift, 16
  %bshift = shl i32 %b, 16
  %bhalf = ashr i32 %bshift, 16
  %product = mul i32 %ahalf, %bhalf
  %rounded = add i32 %product, 536870912
  %result = ashr i32 %rounded, 30
  ret i32 %result
}

define i32 @mulsrn_31(i32 %a, i32 %b) {
; CHECK-LABEL: mulsrn_31:
; CHECK: seal5.cv.mulsrn {{.*}}, 31{{$}}
; CHECK: ret
  %ashift = shl i32 %a, 16
  %ahalf = ashr i32 %ashift, 16
  %bshift = shl i32 %b, 16
  %bhalf = ashr i32 %bshift, 16
  %product = mul i32 %ahalf, %bhalf
  %rounded = add i32 %product, 1073741824
  %result = ashr i32 %rounded, 31
  ret i32 %result
}

; RUN: llc -O0 -mtriple=riscv32 -mattr=+m,+xcorevmac -verify-machineinstrs -global-isel=0 < %s | FileCheck %s
; RUN: llc -O3 -mtriple=riscv32 -mattr=+m,+xcorevmac -verify-machineinstrs -global-isel=0 < %s | FileCheck %s
; RUN: llc -O0 -mtriple=riscv32 -mattr=+m,+xcorevmac -verify-machineinstrs -global-isel=1 -global-isel-abort=1 < %s | FileCheck %s
; RUN: llc -O3 -mtriple=riscv32 -mattr=+m,+xcorevmac -verify-machineinstrs -global-isel=1 -global-isel-abort=1 < %s | FileCheck %s

define i32 @mulsN_1(i32 %a, i32 %b) {
; CHECK-LABEL: mulsN_1:
; CHECK: seal5.cv.mulsn {{[^,]+}}, {{[^,]+}}, {{[^,]+}}, 1{{$}}
; CHECK: ret
  %1 = shl i32 %a, 16
  %2 = ashr i32 %1, 16
  %3 = shl i32 %b, 16
  %4 = ashr i32 %3, 16
  %5 = mul i32 %2, %4
  %6 = ashr i32 %5, 1
  ret i32 %6
}

define i32 @mulsN_2(i32 %a, i32 %b) {
; CHECK-LABEL: mulsN_2:
; CHECK: seal5.cv.mulsn {{[^,]+}}, {{[^,]+}}, {{[^,]+}}, 2{{$}}
; CHECK: ret
  %1 = shl i32 %a, 16
  %2 = ashr i32 %1, 16
  %3 = shl i32 %b, 16
  %4 = ashr i32 %3, 16
  %5 = mul i32 %2, %4
  %6 = ashr i32 %5, 2
  ret i32 %6
}

define i32 @mulsN_3(i32 %a, i32 %b) {
; CHECK-LABEL: mulsN_3:
; CHECK: seal5.cv.mulsn {{[^,]+}}, {{[^,]+}}, {{[^,]+}}, 3{{$}}
; CHECK: ret
  %1 = shl i32 %a, 16
  %2 = ashr i32 %1, 16
  %3 = shl i32 %b, 16
  %4 = ashr i32 %3, 16
  %5 = mul i32 %2, %4
  %6 = ashr i32 %5, 3
  ret i32 %6
}

define i32 @mulsN_4(i32 %a, i32 %b) {
; CHECK-LABEL: mulsN_4:
; CHECK: seal5.cv.mulsn {{[^,]+}}, {{[^,]+}}, {{[^,]+}}, 4{{$}}
; CHECK: ret
  %1 = shl i32 %a, 16
  %2 = ashr i32 %1, 16
  %3 = shl i32 %b, 16
  %4 = ashr i32 %3, 16
  %5 = mul i32 %2, %4
  %6 = ashr i32 %5, 4
  ret i32 %6
}

define i32 @mulsN_5(i32 %a, i32 %b) {
; CHECK-LABEL: mulsN_5:
; CHECK: seal5.cv.mulsn {{[^,]+}}, {{[^,]+}}, {{[^,]+}}, 5{{$}}
; CHECK: ret
  %1 = shl i32 %a, 16
  %2 = ashr i32 %1, 16
  %3 = shl i32 %b, 16
  %4 = ashr i32 %3, 16
  %5 = mul i32 %2, %4
  %6 = ashr i32 %5, 5
  ret i32 %6
}

define i32 @mulsN_6(i32 %a, i32 %b) {
; CHECK-LABEL: mulsN_6:
; CHECK: seal5.cv.mulsn {{[^,]+}}, {{[^,]+}}, {{[^,]+}}, 6{{$}}
; CHECK: ret
  %1 = shl i32 %a, 16
  %2 = ashr i32 %1, 16
  %3 = shl i32 %b, 16
  %4 = ashr i32 %3, 16
  %5 = mul i32 %2, %4
  %6 = ashr i32 %5, 6
  ret i32 %6
}

define i32 @mulsN_7(i32 %a, i32 %b) {
; CHECK-LABEL: mulsN_7:
; CHECK: seal5.cv.mulsn {{[^,]+}}, {{[^,]+}}, {{[^,]+}}, 7{{$}}
; CHECK: ret
  %1 = shl i32 %a, 16
  %2 = ashr i32 %1, 16
  %3 = shl i32 %b, 16
  %4 = ashr i32 %3, 16
  %5 = mul i32 %2, %4
  %6 = ashr i32 %5, 7
  ret i32 %6
}

define i32 @mulsN_8(i32 %a, i32 %b) {
; CHECK-LABEL: mulsN_8:
; CHECK: seal5.cv.mulsn {{[^,]+}}, {{[^,]+}}, {{[^,]+}}, 8{{$}}
; CHECK: ret
  %1 = shl i32 %a, 16
  %2 = ashr i32 %1, 16
  %3 = shl i32 %b, 16
  %4 = ashr i32 %3, 16
  %5 = mul i32 %2, %4
  %6 = ashr i32 %5, 8
  ret i32 %6
}

define i32 @mulsN_9(i32 %a, i32 %b) {
; CHECK-LABEL: mulsN_9:
; CHECK: seal5.cv.mulsn {{[^,]+}}, {{[^,]+}}, {{[^,]+}}, 9{{$}}
; CHECK: ret
  %1 = shl i32 %a, 16
  %2 = ashr i32 %1, 16
  %3 = shl i32 %b, 16
  %4 = ashr i32 %3, 16
  %5 = mul i32 %2, %4
  %6 = ashr i32 %5, 9
  ret i32 %6
}

define i32 @mulsN_10(i32 %a, i32 %b) {
; CHECK-LABEL: mulsN_10:
; CHECK: seal5.cv.mulsn {{[^,]+}}, {{[^,]+}}, {{[^,]+}}, 10{{$}}
; CHECK: ret
  %1 = shl i32 %a, 16
  %2 = ashr i32 %1, 16
  %3 = shl i32 %b, 16
  %4 = ashr i32 %3, 16
  %5 = mul i32 %2, %4
  %6 = ashr i32 %5, 10
  ret i32 %6
}

define i32 @mulsN_11(i32 %a, i32 %b) {
; CHECK-LABEL: mulsN_11:
; CHECK: seal5.cv.mulsn {{[^,]+}}, {{[^,]+}}, {{[^,]+}}, 11{{$}}
; CHECK: ret
  %1 = shl i32 %a, 16
  %2 = ashr i32 %1, 16
  %3 = shl i32 %b, 16
  %4 = ashr i32 %3, 16
  %5 = mul i32 %2, %4
  %6 = ashr i32 %5, 11
  ret i32 %6
}

define i32 @mulsN_12(i32 %a, i32 %b) {
; CHECK-LABEL: mulsN_12:
; CHECK: seal5.cv.mulsn {{[^,]+}}, {{[^,]+}}, {{[^,]+}}, 12{{$}}
; CHECK: ret
  %1 = shl i32 %a, 16
  %2 = ashr i32 %1, 16
  %3 = shl i32 %b, 16
  %4 = ashr i32 %3, 16
  %5 = mul i32 %2, %4
  %6 = ashr i32 %5, 12
  ret i32 %6
}

define i32 @mulsN_13(i32 %a, i32 %b) {
; CHECK-LABEL: mulsN_13:
; CHECK: seal5.cv.mulsn {{[^,]+}}, {{[^,]+}}, {{[^,]+}}, 13{{$}}
; CHECK: ret
  %1 = shl i32 %a, 16
  %2 = ashr i32 %1, 16
  %3 = shl i32 %b, 16
  %4 = ashr i32 %3, 16
  %5 = mul i32 %2, %4
  %6 = ashr i32 %5, 13
  ret i32 %6
}

define i32 @mulsN_14(i32 %a, i32 %b) {
; CHECK-LABEL: mulsN_14:
; CHECK: seal5.cv.mulsn {{[^,]+}}, {{[^,]+}}, {{[^,]+}}, 14{{$}}
; CHECK: ret
  %1 = shl i32 %a, 16
  %2 = ashr i32 %1, 16
  %3 = shl i32 %b, 16
  %4 = ashr i32 %3, 16
  %5 = mul i32 %2, %4
  %6 = ashr i32 %5, 14
  ret i32 %6
}

define i32 @mulsN_15(i32 %a, i32 %b) {
; CHECK-LABEL: mulsN_15:
; CHECK: seal5.cv.mulsn {{[^,]+}}, {{[^,]+}}, {{[^,]+}}, 15{{$}}
; CHECK: ret
  %1 = shl i32 %a, 16
  %2 = ashr i32 %1, 16
  %3 = shl i32 %b, 16
  %4 = ashr i32 %3, 16
  %5 = mul i32 %2, %4
  %6 = ashr i32 %5, 15
  ret i32 %6
}

define i32 @mulsN_16(i32 %a, i32 %b) {
; CHECK-LABEL: mulsN_16:
; CHECK: seal5.cv.mulsn {{[^,]+}}, {{[^,]+}}, {{[^,]+}}, 16{{$}}
; CHECK: ret
  %1 = shl i32 %a, 16
  %2 = ashr i32 %1, 16
  %3 = shl i32 %b, 16
  %4 = ashr i32 %3, 16
  %5 = mul i32 %2, %4
  %6 = ashr i32 %5, 16
  ret i32 %6
}

define i32 @mulsN_17(i32 %a, i32 %b) {
; CHECK-LABEL: mulsN_17:
; CHECK: seal5.cv.mulsn {{[^,]+}}, {{[^,]+}}, {{[^,]+}}, 17{{$}}
; CHECK: ret
  %1 = shl i32 %a, 16
  %2 = ashr i32 %1, 16
  %3 = shl i32 %b, 16
  %4 = ashr i32 %3, 16
  %5 = mul i32 %2, %4
  %6 = ashr i32 %5, 17
  ret i32 %6
}

define i32 @mulsN_18(i32 %a, i32 %b) {
; CHECK-LABEL: mulsN_18:
; CHECK: seal5.cv.mulsn {{[^,]+}}, {{[^,]+}}, {{[^,]+}}, 18{{$}}
; CHECK: ret
  %1 = shl i32 %a, 16
  %2 = ashr i32 %1, 16
  %3 = shl i32 %b, 16
  %4 = ashr i32 %3, 16
  %5 = mul i32 %2, %4
  %6 = ashr i32 %5, 18
  ret i32 %6
}

define i32 @mulsN_19(i32 %a, i32 %b) {
; CHECK-LABEL: mulsN_19:
; CHECK: seal5.cv.mulsn {{[^,]+}}, {{[^,]+}}, {{[^,]+}}, 19{{$}}
; CHECK: ret
  %1 = shl i32 %a, 16
  %2 = ashr i32 %1, 16
  %3 = shl i32 %b, 16
  %4 = ashr i32 %3, 16
  %5 = mul i32 %2, %4
  %6 = ashr i32 %5, 19
  ret i32 %6
}

define i32 @mulsN_20(i32 %a, i32 %b) {
; CHECK-LABEL: mulsN_20:
; CHECK: seal5.cv.mulsn {{[^,]+}}, {{[^,]+}}, {{[^,]+}}, 20{{$}}
; CHECK: ret
  %1 = shl i32 %a, 16
  %2 = ashr i32 %1, 16
  %3 = shl i32 %b, 16
  %4 = ashr i32 %3, 16
  %5 = mul i32 %2, %4
  %6 = ashr i32 %5, 20
  ret i32 %6
}

define i32 @mulsN_21(i32 %a, i32 %b) {
; CHECK-LABEL: mulsN_21:
; CHECK: seal5.cv.mulsn {{[^,]+}}, {{[^,]+}}, {{[^,]+}}, 21{{$}}
; CHECK: ret
  %1 = shl i32 %a, 16
  %2 = ashr i32 %1, 16
  %3 = shl i32 %b, 16
  %4 = ashr i32 %3, 16
  %5 = mul i32 %2, %4
  %6 = ashr i32 %5, 21
  ret i32 %6
}

define i32 @mulsN_22(i32 %a, i32 %b) {
; CHECK-LABEL: mulsN_22:
; CHECK: seal5.cv.mulsn {{[^,]+}}, {{[^,]+}}, {{[^,]+}}, 22{{$}}
; CHECK: ret
  %1 = shl i32 %a, 16
  %2 = ashr i32 %1, 16
  %3 = shl i32 %b, 16
  %4 = ashr i32 %3, 16
  %5 = mul i32 %2, %4
  %6 = ashr i32 %5, 22
  ret i32 %6
}

define i32 @mulsN_23(i32 %a, i32 %b) {
; CHECK-LABEL: mulsN_23:
; CHECK: seal5.cv.mulsn {{[^,]+}}, {{[^,]+}}, {{[^,]+}}, 23{{$}}
; CHECK: ret
  %1 = shl i32 %a, 16
  %2 = ashr i32 %1, 16
  %3 = shl i32 %b, 16
  %4 = ashr i32 %3, 16
  %5 = mul i32 %2, %4
  %6 = ashr i32 %5, 23
  ret i32 %6
}

define i32 @mulsN_24(i32 %a, i32 %b) {
; CHECK-LABEL: mulsN_24:
; CHECK: seal5.cv.mulsn {{[^,]+}}, {{[^,]+}}, {{[^,]+}}, 24{{$}}
; CHECK: ret
  %1 = shl i32 %a, 16
  %2 = ashr i32 %1, 16
  %3 = shl i32 %b, 16
  %4 = ashr i32 %3, 16
  %5 = mul i32 %2, %4
  %6 = ashr i32 %5, 24
  ret i32 %6
}

define i32 @mulsN_25(i32 %a, i32 %b) {
; CHECK-LABEL: mulsN_25:
; CHECK: seal5.cv.mulsn {{[^,]+}}, {{[^,]+}}, {{[^,]+}}, 25{{$}}
; CHECK: ret
  %1 = shl i32 %a, 16
  %2 = ashr i32 %1, 16
  %3 = shl i32 %b, 16
  %4 = ashr i32 %3, 16
  %5 = mul i32 %2, %4
  %6 = ashr i32 %5, 25
  ret i32 %6
}

define i32 @mulsN_26(i32 %a, i32 %b) {
; CHECK-LABEL: mulsN_26:
; CHECK: seal5.cv.mulsn {{[^,]+}}, {{[^,]+}}, {{[^,]+}}, 26{{$}}
; CHECK: ret
  %1 = shl i32 %a, 16
  %2 = ashr i32 %1, 16
  %3 = shl i32 %b, 16
  %4 = ashr i32 %3, 16
  %5 = mul i32 %2, %4
  %6 = ashr i32 %5, 26
  ret i32 %6
}

define i32 @mulsN_27(i32 %a, i32 %b) {
; CHECK-LABEL: mulsN_27:
; CHECK: seal5.cv.mulsn {{[^,]+}}, {{[^,]+}}, {{[^,]+}}, 27{{$}}
; CHECK: ret
  %1 = shl i32 %a, 16
  %2 = ashr i32 %1, 16
  %3 = shl i32 %b, 16
  %4 = ashr i32 %3, 16
  %5 = mul i32 %2, %4
  %6 = ashr i32 %5, 27
  ret i32 %6
}

define i32 @mulsN_28(i32 %a, i32 %b) {
; CHECK-LABEL: mulsN_28:
; CHECK: seal5.cv.mulsn {{[^,]+}}, {{[^,]+}}, {{[^,]+}}, 28{{$}}
; CHECK: ret
  %1 = shl i32 %a, 16
  %2 = ashr i32 %1, 16
  %3 = shl i32 %b, 16
  %4 = ashr i32 %3, 16
  %5 = mul i32 %2, %4
  %6 = ashr i32 %5, 28
  ret i32 %6
}

define i32 @mulsN_29(i32 %a, i32 %b) {
; CHECK-LABEL: mulsN_29:
; CHECK: seal5.cv.mulsn {{[^,]+}}, {{[^,]+}}, {{[^,]+}}, 29{{$}}
; CHECK: ret
  %1 = shl i32 %a, 16
  %2 = ashr i32 %1, 16
  %3 = shl i32 %b, 16
  %4 = ashr i32 %3, 16
  %5 = mul i32 %2, %4
  %6 = ashr i32 %5, 29
  ret i32 %6
}

define i32 @mulsN_30(i32 %a, i32 %b) {
; CHECK-LABEL: mulsN_30:
; CHECK: seal5.cv.mulsn {{[^,]+}}, {{[^,]+}}, {{[^,]+}}, 30{{$}}
; CHECK: ret
  %1 = shl i32 %a, 16
  %2 = ashr i32 %1, 16
  %3 = shl i32 %b, 16
  %4 = ashr i32 %3, 16
  %5 = mul i32 %2, %4
  %6 = ashr i32 %5, 30
  ret i32 %6
}

define i32 @mulsN_31(i32 %a, i32 %b) {
; CHECK-LABEL: mulsN_31:
; CHECK: seal5.cv.mulsn {{[^,]+}}, {{[^,]+}}, {{[^,]+}}, 31{{$}}
; CHECK: ret
  %1 = shl i32 %a, 16
  %2 = ashr i32 %1, 16
  %3 = shl i32 %b, 16
  %4 = ashr i32 %3, 16
  %5 = mul i32 %2, %4
  %6 = ashr i32 %5, 31
  ret i32 %6
}

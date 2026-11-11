; RUN: llc -O0 -mtriple=riscv32 -mattr=+m,+xcorevmac -verify-machineinstrs -global-isel=0 < %s | FileCheck %s
; RUN: llc -O3 -mtriple=riscv32 -mattr=+m,+xcorevmac -verify-machineinstrs -global-isel=0 < %s | FileCheck %s
; RUN: llc -O0 -mtriple=riscv32 -mattr=+m,+xcorevmac -verify-machineinstrs -global-isel=1 -global-isel-abort=1 < %s | FileCheck %s
; RUN: llc -O3 -mtriple=riscv32 -mattr=+m,+xcorevmac -verify-machineinstrs -global-isel=1 -global-isel-abort=1 < %s | FileCheck %s

define i32 @muluN_1(i32 %a, i32 %b) {
; CHECK-LABEL: muluN_1:
; CHECK: seal5.cv.mulun {{[^,]+}}, {{[^,]+}}, {{[^,]+}}, 1{{$}}
; CHECK: ret
  %1 = and i32 %a, 65535
  %2 = and i32 %b, 65535
  %3 = mul i32 %1, %2
  %4 = lshr i32 %3, 1
  ret i32 %4
}

define i32 @muluN_2(i32 %a, i32 %b) {
; CHECK-LABEL: muluN_2:
; CHECK: seal5.cv.mulun {{[^,]+}}, {{[^,]+}}, {{[^,]+}}, 2{{$}}
; CHECK: ret
  %1 = and i32 %a, 65535
  %2 = and i32 %b, 65535
  %3 = mul i32 %1, %2
  %4 = lshr i32 %3, 2
  ret i32 %4
}

define i32 @muluN_3(i32 %a, i32 %b) {
; CHECK-LABEL: muluN_3:
; CHECK: seal5.cv.mulun {{[^,]+}}, {{[^,]+}}, {{[^,]+}}, 3{{$}}
; CHECK: ret
  %1 = and i32 %a, 65535
  %2 = and i32 %b, 65535
  %3 = mul i32 %1, %2
  %4 = lshr i32 %3, 3
  ret i32 %4
}

define i32 @muluN_4(i32 %a, i32 %b) {
; CHECK-LABEL: muluN_4:
; CHECK: seal5.cv.mulun {{[^,]+}}, {{[^,]+}}, {{[^,]+}}, 4{{$}}
; CHECK: ret
  %1 = and i32 %a, 65535
  %2 = and i32 %b, 65535
  %3 = mul i32 %1, %2
  %4 = lshr i32 %3, 4
  ret i32 %4
}

define i32 @muluN_5(i32 %a, i32 %b) {
; CHECK-LABEL: muluN_5:
; CHECK: seal5.cv.mulun {{[^,]+}}, {{[^,]+}}, {{[^,]+}}, 5{{$}}
; CHECK: ret
  %1 = and i32 %a, 65535
  %2 = and i32 %b, 65535
  %3 = mul i32 %1, %2
  %4 = lshr i32 %3, 5
  ret i32 %4
}

define i32 @muluN_6(i32 %a, i32 %b) {
; CHECK-LABEL: muluN_6:
; CHECK: seal5.cv.mulun {{[^,]+}}, {{[^,]+}}, {{[^,]+}}, 6{{$}}
; CHECK: ret
  %1 = and i32 %a, 65535
  %2 = and i32 %b, 65535
  %3 = mul i32 %1, %2
  %4 = lshr i32 %3, 6
  ret i32 %4
}

define i32 @muluN_7(i32 %a, i32 %b) {
; CHECK-LABEL: muluN_7:
; CHECK: seal5.cv.mulun {{[^,]+}}, {{[^,]+}}, {{[^,]+}}, 7{{$}}
; CHECK: ret
  %1 = and i32 %a, 65535
  %2 = and i32 %b, 65535
  %3 = mul i32 %1, %2
  %4 = lshr i32 %3, 7
  ret i32 %4
}

define i32 @muluN_8(i32 %a, i32 %b) {
; CHECK-LABEL: muluN_8:
; CHECK: seal5.cv.mulun {{[^,]+}}, {{[^,]+}}, {{[^,]+}}, 8{{$}}
; CHECK: ret
  %1 = and i32 %a, 65535
  %2 = and i32 %b, 65535
  %3 = mul i32 %1, %2
  %4 = lshr i32 %3, 8
  ret i32 %4
}

define i32 @muluN_9(i32 %a, i32 %b) {
; CHECK-LABEL: muluN_9:
; CHECK: seal5.cv.mulun {{[^,]+}}, {{[^,]+}}, {{[^,]+}}, 9{{$}}
; CHECK: ret
  %1 = and i32 %a, 65535
  %2 = and i32 %b, 65535
  %3 = mul i32 %1, %2
  %4 = lshr i32 %3, 9
  ret i32 %4
}

define i32 @muluN_10(i32 %a, i32 %b) {
; CHECK-LABEL: muluN_10:
; CHECK: seal5.cv.mulun {{[^,]+}}, {{[^,]+}}, {{[^,]+}}, 10{{$}}
; CHECK: ret
  %1 = and i32 %a, 65535
  %2 = and i32 %b, 65535
  %3 = mul i32 %1, %2
  %4 = lshr i32 %3, 10
  ret i32 %4
}

define i32 @muluN_11(i32 %a, i32 %b) {
; CHECK-LABEL: muluN_11:
; CHECK: seal5.cv.mulun {{[^,]+}}, {{[^,]+}}, {{[^,]+}}, 11{{$}}
; CHECK: ret
  %1 = and i32 %a, 65535
  %2 = and i32 %b, 65535
  %3 = mul i32 %1, %2
  %4 = lshr i32 %3, 11
  ret i32 %4
}

define i32 @muluN_12(i32 %a, i32 %b) {
; CHECK-LABEL: muluN_12:
; CHECK: seal5.cv.mulun {{[^,]+}}, {{[^,]+}}, {{[^,]+}}, 12{{$}}
; CHECK: ret
  %1 = and i32 %a, 65535
  %2 = and i32 %b, 65535
  %3 = mul i32 %1, %2
  %4 = lshr i32 %3, 12
  ret i32 %4
}

define i32 @muluN_13(i32 %a, i32 %b) {
; CHECK-LABEL: muluN_13:
; CHECK: seal5.cv.mulun {{[^,]+}}, {{[^,]+}}, {{[^,]+}}, 13{{$}}
; CHECK: ret
  %1 = and i32 %a, 65535
  %2 = and i32 %b, 65535
  %3 = mul i32 %1, %2
  %4 = lshr i32 %3, 13
  ret i32 %4
}

define i32 @muluN_14(i32 %a, i32 %b) {
; CHECK-LABEL: muluN_14:
; CHECK: seal5.cv.mulun {{[^,]+}}, {{[^,]+}}, {{[^,]+}}, 14{{$}}
; CHECK: ret
  %1 = and i32 %a, 65535
  %2 = and i32 %b, 65535
  %3 = mul i32 %1, %2
  %4 = lshr i32 %3, 14
  ret i32 %4
}

define i32 @muluN_15(i32 %a, i32 %b) {
; CHECK-LABEL: muluN_15:
; CHECK: seal5.cv.mulun {{[^,]+}}, {{[^,]+}}, {{[^,]+}}, 15{{$}}
; CHECK: ret
  %1 = and i32 %a, 65535
  %2 = and i32 %b, 65535
  %3 = mul i32 %1, %2
  %4 = lshr i32 %3, 15
  ret i32 %4
}

define i32 @muluN_16(i32 %a, i32 %b) {
; CHECK-LABEL: muluN_16:
; CHECK: seal5.cv.mulun {{[^,]+}}, {{[^,]+}}, {{[^,]+}}, 16{{$}}
; CHECK: ret
  %1 = and i32 %a, 65535
  %2 = and i32 %b, 65535
  %3 = mul i32 %1, %2
  %4 = lshr i32 %3, 16
  ret i32 %4
}

define i32 @muluN_17(i32 %a, i32 %b) {
; CHECK-LABEL: muluN_17:
; CHECK: seal5.cv.mulun {{[^,]+}}, {{[^,]+}}, {{[^,]+}}, 17{{$}}
; CHECK: ret
  %1 = and i32 %a, 65535
  %2 = and i32 %b, 65535
  %3 = mul i32 %1, %2
  %4 = lshr i32 %3, 17
  ret i32 %4
}

define i32 @muluN_18(i32 %a, i32 %b) {
; CHECK-LABEL: muluN_18:
; CHECK: seal5.cv.mulun {{[^,]+}}, {{[^,]+}}, {{[^,]+}}, 18{{$}}
; CHECK: ret
  %1 = and i32 %a, 65535
  %2 = and i32 %b, 65535
  %3 = mul i32 %1, %2
  %4 = lshr i32 %3, 18
  ret i32 %4
}

define i32 @muluN_19(i32 %a, i32 %b) {
; CHECK-LABEL: muluN_19:
; CHECK: seal5.cv.mulun {{[^,]+}}, {{[^,]+}}, {{[^,]+}}, 19{{$}}
; CHECK: ret
  %1 = and i32 %a, 65535
  %2 = and i32 %b, 65535
  %3 = mul i32 %1, %2
  %4 = lshr i32 %3, 19
  ret i32 %4
}

define i32 @muluN_20(i32 %a, i32 %b) {
; CHECK-LABEL: muluN_20:
; CHECK: seal5.cv.mulun {{[^,]+}}, {{[^,]+}}, {{[^,]+}}, 20{{$}}
; CHECK: ret
  %1 = and i32 %a, 65535
  %2 = and i32 %b, 65535
  %3 = mul i32 %1, %2
  %4 = lshr i32 %3, 20
  ret i32 %4
}

define i32 @muluN_21(i32 %a, i32 %b) {
; CHECK-LABEL: muluN_21:
; CHECK: seal5.cv.mulun {{[^,]+}}, {{[^,]+}}, {{[^,]+}}, 21{{$}}
; CHECK: ret
  %1 = and i32 %a, 65535
  %2 = and i32 %b, 65535
  %3 = mul i32 %1, %2
  %4 = lshr i32 %3, 21
  ret i32 %4
}

define i32 @muluN_22(i32 %a, i32 %b) {
; CHECK-LABEL: muluN_22:
; CHECK: seal5.cv.mulun {{[^,]+}}, {{[^,]+}}, {{[^,]+}}, 22{{$}}
; CHECK: ret
  %1 = and i32 %a, 65535
  %2 = and i32 %b, 65535
  %3 = mul i32 %1, %2
  %4 = lshr i32 %3, 22
  ret i32 %4
}

define i32 @muluN_23(i32 %a, i32 %b) {
; CHECK-LABEL: muluN_23:
; CHECK: seal5.cv.mulun {{[^,]+}}, {{[^,]+}}, {{[^,]+}}, 23{{$}}
; CHECK: ret
  %1 = and i32 %a, 65535
  %2 = and i32 %b, 65535
  %3 = mul i32 %1, %2
  %4 = lshr i32 %3, 23
  ret i32 %4
}

define i32 @muluN_24(i32 %a, i32 %b) {
; CHECK-LABEL: muluN_24:
; CHECK: seal5.cv.mulun {{[^,]+}}, {{[^,]+}}, {{[^,]+}}, 24{{$}}
; CHECK: ret
  %1 = and i32 %a, 65535
  %2 = and i32 %b, 65535
  %3 = mul i32 %1, %2
  %4 = lshr i32 %3, 24
  ret i32 %4
}

define i32 @muluN_25(i32 %a, i32 %b) {
; CHECK-LABEL: muluN_25:
; CHECK: seal5.cv.mulun {{[^,]+}}, {{[^,]+}}, {{[^,]+}}, 25{{$}}
; CHECK: ret
  %1 = and i32 %a, 65535
  %2 = and i32 %b, 65535
  %3 = mul i32 %1, %2
  %4 = lshr i32 %3, 25
  ret i32 %4
}

define i32 @muluN_26(i32 %a, i32 %b) {
; CHECK-LABEL: muluN_26:
; CHECK: seal5.cv.mulun {{[^,]+}}, {{[^,]+}}, {{[^,]+}}, 26{{$}}
; CHECK: ret
  %1 = and i32 %a, 65535
  %2 = and i32 %b, 65535
  %3 = mul i32 %1, %2
  %4 = lshr i32 %3, 26
  ret i32 %4
}

define i32 @muluN_27(i32 %a, i32 %b) {
; CHECK-LABEL: muluN_27:
; CHECK: seal5.cv.mulun {{[^,]+}}, {{[^,]+}}, {{[^,]+}}, 27{{$}}
; CHECK: ret
  %1 = and i32 %a, 65535
  %2 = and i32 %b, 65535
  %3 = mul i32 %1, %2
  %4 = lshr i32 %3, 27
  ret i32 %4
}

define i32 @muluN_28(i32 %a, i32 %b) {
; CHECK-LABEL: muluN_28:
; CHECK: seal5.cv.mulun {{[^,]+}}, {{[^,]+}}, {{[^,]+}}, 28{{$}}
; CHECK: ret
  %1 = and i32 %a, 65535
  %2 = and i32 %b, 65535
  %3 = mul i32 %1, %2
  %4 = lshr i32 %3, 28
  ret i32 %4
}

define i32 @muluN_29(i32 %a, i32 %b) {
; CHECK-LABEL: muluN_29:
; CHECK: seal5.cv.mulun {{[^,]+}}, {{[^,]+}}, {{[^,]+}}, 29{{$}}
; CHECK: ret
  %1 = and i32 %a, 65535
  %2 = and i32 %b, 65535
  %3 = mul i32 %1, %2
  %4 = lshr i32 %3, 29
  ret i32 %4
}

define i32 @muluN_30(i32 %a, i32 %b) {
; CHECK-LABEL: muluN_30:
; CHECK: seal5.cv.mulun {{[^,]+}}, {{[^,]+}}, {{[^,]+}}, 30{{$}}
; CHECK: ret
  %1 = and i32 %a, 65535
  %2 = and i32 %b, 65535
  %3 = mul i32 %1, %2
  %4 = lshr i32 %3, 30
  ret i32 %4
}

define i32 @muluN_31(i32 %a, i32 %b) {
; CHECK-LABEL: muluN_31:
; CHECK: seal5.cv.mulun {{[^,]+}}, {{[^,]+}}, {{[^,]+}}, 31{{$}}
; CHECK: ret
  %1 = and i32 %a, 65535
  %2 = and i32 %b, 65535
  %3 = mul i32 %1, %2
  %4 = lshr i32 %3, 31
  ret i32 %4
}

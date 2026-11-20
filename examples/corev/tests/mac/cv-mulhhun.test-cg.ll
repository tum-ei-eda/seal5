; RUN: llc -O0 -mtriple=riscv32 -mattr=+m,+xcorevmac -verify-machineinstrs -global-isel=0 < %s | FileCheck %s
; RUN: llc -O3 -mtriple=riscv32 -mattr=+m,+xcorevmac -verify-machineinstrs -global-isel=0 < %s | FileCheck %s
; RUN: llc -O0 -mtriple=riscv32 -mattr=+m,+xcorevmac -verify-machineinstrs -global-isel=1 -global-isel-abort=1 < %s | FileCheck %s
; RUN: llc -O3 -mtriple=riscv32 -mattr=+m,+xcorevmac -verify-machineinstrs -global-isel=1 -global-isel-abort=1 < %s | FileCheck %s

define i32 @mulhhuN_1(i32 %a, i32 %b) {
; CHECK-LABEL: mulhhuN_1:
; CHECK: seal5.cv.mulhhun {{[^,]+}}, {{[^,]+}}, {{[^,]+}}, 1{{$}}
; CHECK: ret
  %1 = lshr i32 %a, 16
  %2 = lshr i32 %b, 16
  %3 = mul i32 %1, %2
  %4 = lshr i32 %3, 1
  ret i32 %4
}

define i32 @mulhhuN_2(i32 %a, i32 %b) {
; CHECK-LABEL: mulhhuN_2:
; CHECK: seal5.cv.mulhhun {{[^,]+}}, {{[^,]+}}, {{[^,]+}}, 2{{$}}
; CHECK: ret
  %1 = lshr i32 %a, 16
  %2 = lshr i32 %b, 16
  %3 = mul i32 %1, %2
  %4 = lshr i32 %3, 2
  ret i32 %4
}

define i32 @mulhhuN_3(i32 %a, i32 %b) {
; CHECK-LABEL: mulhhuN_3:
; CHECK: seal5.cv.mulhhun {{[^,]+}}, {{[^,]+}}, {{[^,]+}}, 3{{$}}
; CHECK: ret
  %1 = lshr i32 %a, 16
  %2 = lshr i32 %b, 16
  %3 = mul i32 %1, %2
  %4 = lshr i32 %3, 3
  ret i32 %4
}

define i32 @mulhhuN_4(i32 %a, i32 %b) {
; CHECK-LABEL: mulhhuN_4:
; CHECK: seal5.cv.mulhhun {{[^,]+}}, {{[^,]+}}, {{[^,]+}}, 4{{$}}
; CHECK: ret
  %1 = lshr i32 %a, 16
  %2 = lshr i32 %b, 16
  %3 = mul i32 %1, %2
  %4 = lshr i32 %3, 4
  ret i32 %4
}

define i32 @mulhhuN_5(i32 %a, i32 %b) {
; CHECK-LABEL: mulhhuN_5:
; CHECK: seal5.cv.mulhhun {{[^,]+}}, {{[^,]+}}, {{[^,]+}}, 5{{$}}
; CHECK: ret
  %1 = lshr i32 %a, 16
  %2 = lshr i32 %b, 16
  %3 = mul i32 %1, %2
  %4 = lshr i32 %3, 5
  ret i32 %4
}

define i32 @mulhhuN_6(i32 %a, i32 %b) {
; CHECK-LABEL: mulhhuN_6:
; CHECK: seal5.cv.mulhhun {{[^,]+}}, {{[^,]+}}, {{[^,]+}}, 6{{$}}
; CHECK: ret
  %1 = lshr i32 %a, 16
  %2 = lshr i32 %b, 16
  %3 = mul i32 %1, %2
  %4 = lshr i32 %3, 6
  ret i32 %4
}

define i32 @mulhhuN_7(i32 %a, i32 %b) {
; CHECK-LABEL: mulhhuN_7:
; CHECK: seal5.cv.mulhhun {{[^,]+}}, {{[^,]+}}, {{[^,]+}}, 7{{$}}
; CHECK: ret
  %1 = lshr i32 %a, 16
  %2 = lshr i32 %b, 16
  %3 = mul i32 %1, %2
  %4 = lshr i32 %3, 7
  ret i32 %4
}

define i32 @mulhhuN_8(i32 %a, i32 %b) {
; CHECK-LABEL: mulhhuN_8:
; CHECK: seal5.cv.mulhhun {{[^,]+}}, {{[^,]+}}, {{[^,]+}}, 8{{$}}
; CHECK: ret
  %1 = lshr i32 %a, 16
  %2 = lshr i32 %b, 16
  %3 = mul i32 %1, %2
  %4 = lshr i32 %3, 8
  ret i32 %4
}

define i32 @mulhhuN_9(i32 %a, i32 %b) {
; CHECK-LABEL: mulhhuN_9:
; CHECK: seal5.cv.mulhhun {{[^,]+}}, {{[^,]+}}, {{[^,]+}}, 9{{$}}
; CHECK: ret
  %1 = lshr i32 %a, 16
  %2 = lshr i32 %b, 16
  %3 = mul i32 %1, %2
  %4 = lshr i32 %3, 9
  ret i32 %4
}

define i32 @mulhhuN_10(i32 %a, i32 %b) {
; CHECK-LABEL: mulhhuN_10:
; CHECK: seal5.cv.mulhhun {{[^,]+}}, {{[^,]+}}, {{[^,]+}}, 10{{$}}
; CHECK: ret
  %1 = lshr i32 %a, 16
  %2 = lshr i32 %b, 16
  %3 = mul i32 %1, %2
  %4 = lshr i32 %3, 10
  ret i32 %4
}

define i32 @mulhhuN_11(i32 %a, i32 %b) {
; CHECK-LABEL: mulhhuN_11:
; CHECK: seal5.cv.mulhhun {{[^,]+}}, {{[^,]+}}, {{[^,]+}}, 11{{$}}
; CHECK: ret
  %1 = lshr i32 %a, 16
  %2 = lshr i32 %b, 16
  %3 = mul i32 %1, %2
  %4 = lshr i32 %3, 11
  ret i32 %4
}

define i32 @mulhhuN_12(i32 %a, i32 %b) {
; CHECK-LABEL: mulhhuN_12:
; CHECK: seal5.cv.mulhhun {{[^,]+}}, {{[^,]+}}, {{[^,]+}}, 12{{$}}
; CHECK: ret
  %1 = lshr i32 %a, 16
  %2 = lshr i32 %b, 16
  %3 = mul i32 %1, %2
  %4 = lshr i32 %3, 12
  ret i32 %4
}

define i32 @mulhhuN_13(i32 %a, i32 %b) {
; CHECK-LABEL: mulhhuN_13:
; CHECK: seal5.cv.mulhhun {{[^,]+}}, {{[^,]+}}, {{[^,]+}}, 13{{$}}
; CHECK: ret
  %1 = lshr i32 %a, 16
  %2 = lshr i32 %b, 16
  %3 = mul i32 %1, %2
  %4 = lshr i32 %3, 13
  ret i32 %4
}

define i32 @mulhhuN_14(i32 %a, i32 %b) {
; CHECK-LABEL: mulhhuN_14:
; CHECK: seal5.cv.mulhhun {{[^,]+}}, {{[^,]+}}, {{[^,]+}}, 14{{$}}
; CHECK: ret
  %1 = lshr i32 %a, 16
  %2 = lshr i32 %b, 16
  %3 = mul i32 %1, %2
  %4 = lshr i32 %3, 14
  ret i32 %4
}

define i32 @mulhhuN_15(i32 %a, i32 %b) {
; CHECK-LABEL: mulhhuN_15:
; CHECK: seal5.cv.mulhhun {{[^,]+}}, {{[^,]+}}, {{[^,]+}}, 15{{$}}
; CHECK: ret
  %1 = lshr i32 %a, 16
  %2 = lshr i32 %b, 16
  %3 = mul i32 %1, %2
  %4 = lshr i32 %3, 15
  ret i32 %4
}

define i32 @mulhhuN_16(i32 %a, i32 %b) {
; CHECK-LABEL: mulhhuN_16:
; CHECK: seal5.cv.mulhhun {{[^,]+}}, {{[^,]+}}, {{[^,]+}}, 16{{$}}
; CHECK: ret
  %1 = lshr i32 %a, 16
  %2 = lshr i32 %b, 16
  %3 = mul i32 %1, %2
  %4 = lshr i32 %3, 16
  ret i32 %4
}

define i32 @mulhhuN_17(i32 %a, i32 %b) {
; CHECK-LABEL: mulhhuN_17:
; CHECK: seal5.cv.mulhhun {{[^,]+}}, {{[^,]+}}, {{[^,]+}}, 17{{$}}
; CHECK: ret
  %1 = lshr i32 %a, 16
  %2 = lshr i32 %b, 16
  %3 = mul i32 %1, %2
  %4 = lshr i32 %3, 17
  ret i32 %4
}

define i32 @mulhhuN_18(i32 %a, i32 %b) {
; CHECK-LABEL: mulhhuN_18:
; CHECK: seal5.cv.mulhhun {{[^,]+}}, {{[^,]+}}, {{[^,]+}}, 18{{$}}
; CHECK: ret
  %1 = lshr i32 %a, 16
  %2 = lshr i32 %b, 16
  %3 = mul i32 %1, %2
  %4 = lshr i32 %3, 18
  ret i32 %4
}

define i32 @mulhhuN_19(i32 %a, i32 %b) {
; CHECK-LABEL: mulhhuN_19:
; CHECK: seal5.cv.mulhhun {{[^,]+}}, {{[^,]+}}, {{[^,]+}}, 19{{$}}
; CHECK: ret
  %1 = lshr i32 %a, 16
  %2 = lshr i32 %b, 16
  %3 = mul i32 %1, %2
  %4 = lshr i32 %3, 19
  ret i32 %4
}

define i32 @mulhhuN_20(i32 %a, i32 %b) {
; CHECK-LABEL: mulhhuN_20:
; CHECK: seal5.cv.mulhhun {{[^,]+}}, {{[^,]+}}, {{[^,]+}}, 20{{$}}
; CHECK: ret
  %1 = lshr i32 %a, 16
  %2 = lshr i32 %b, 16
  %3 = mul i32 %1, %2
  %4 = lshr i32 %3, 20
  ret i32 %4
}

define i32 @mulhhuN_21(i32 %a, i32 %b) {
; CHECK-LABEL: mulhhuN_21:
; CHECK: seal5.cv.mulhhun {{[^,]+}}, {{[^,]+}}, {{[^,]+}}, 21{{$}}
; CHECK: ret
  %1 = lshr i32 %a, 16
  %2 = lshr i32 %b, 16
  %3 = mul i32 %1, %2
  %4 = lshr i32 %3, 21
  ret i32 %4
}

define i32 @mulhhuN_22(i32 %a, i32 %b) {
; CHECK-LABEL: mulhhuN_22:
; CHECK: seal5.cv.mulhhun {{[^,]+}}, {{[^,]+}}, {{[^,]+}}, 22{{$}}
; CHECK: ret
  %1 = lshr i32 %a, 16
  %2 = lshr i32 %b, 16
  %3 = mul i32 %1, %2
  %4 = lshr i32 %3, 22
  ret i32 %4
}

define i32 @mulhhuN_23(i32 %a, i32 %b) {
; CHECK-LABEL: mulhhuN_23:
; CHECK: seal5.cv.mulhhun {{[^,]+}}, {{[^,]+}}, {{[^,]+}}, 23{{$}}
; CHECK: ret
  %1 = lshr i32 %a, 16
  %2 = lshr i32 %b, 16
  %3 = mul i32 %1, %2
  %4 = lshr i32 %3, 23
  ret i32 %4
}

define i32 @mulhhuN_24(i32 %a, i32 %b) {
; CHECK-LABEL: mulhhuN_24:
; CHECK: seal5.cv.mulhhun {{[^,]+}}, {{[^,]+}}, {{[^,]+}}, 24{{$}}
; CHECK: ret
  %1 = lshr i32 %a, 16
  %2 = lshr i32 %b, 16
  %3 = mul i32 %1, %2
  %4 = lshr i32 %3, 24
  ret i32 %4
}

define i32 @mulhhuN_25(i32 %a, i32 %b) {
; CHECK-LABEL: mulhhuN_25:
; CHECK: seal5.cv.mulhhun {{[^,]+}}, {{[^,]+}}, {{[^,]+}}, 25{{$}}
; CHECK: ret
  %1 = lshr i32 %a, 16
  %2 = lshr i32 %b, 16
  %3 = mul i32 %1, %2
  %4 = lshr i32 %3, 25
  ret i32 %4
}

define i32 @mulhhuN_26(i32 %a, i32 %b) {
; CHECK-LABEL: mulhhuN_26:
; CHECK: seal5.cv.mulhhun {{[^,]+}}, {{[^,]+}}, {{[^,]+}}, 26{{$}}
; CHECK: ret
  %1 = lshr i32 %a, 16
  %2 = lshr i32 %b, 16
  %3 = mul i32 %1, %2
  %4 = lshr i32 %3, 26
  ret i32 %4
}

define i32 @mulhhuN_27(i32 %a, i32 %b) {
; CHECK-LABEL: mulhhuN_27:
; CHECK: seal5.cv.mulhhun {{[^,]+}}, {{[^,]+}}, {{[^,]+}}, 27{{$}}
; CHECK: ret
  %1 = lshr i32 %a, 16
  %2 = lshr i32 %b, 16
  %3 = mul i32 %1, %2
  %4 = lshr i32 %3, 27
  ret i32 %4
}

define i32 @mulhhuN_28(i32 %a, i32 %b) {
; CHECK-LABEL: mulhhuN_28:
; CHECK: seal5.cv.mulhhun {{[^,]+}}, {{[^,]+}}, {{[^,]+}}, 28{{$}}
; CHECK: ret
  %1 = lshr i32 %a, 16
  %2 = lshr i32 %b, 16
  %3 = mul i32 %1, %2
  %4 = lshr i32 %3, 28
  ret i32 %4
}

define i32 @mulhhuN_29(i32 %a, i32 %b) {
; CHECK-LABEL: mulhhuN_29:
; CHECK: seal5.cv.mulhhun {{[^,]+}}, {{[^,]+}}, {{[^,]+}}, 29{{$}}
; CHECK: ret
  %1 = lshr i32 %a, 16
  %2 = lshr i32 %b, 16
  %3 = mul i32 %1, %2
  %4 = lshr i32 %3, 29
  ret i32 %4
}

define i32 @mulhhuN_30(i32 %a, i32 %b) {
; CHECK-LABEL: mulhhuN_30:
; CHECK: seal5.cv.mulhhun {{[^,]+}}, {{[^,]+}}, {{[^,]+}}, 30{{$}}
; CHECK: ret
  %1 = lshr i32 %a, 16
  %2 = lshr i32 %b, 16
  %3 = mul i32 %1, %2
  %4 = lshr i32 %3, 30
  ret i32 %4
}

define i32 @mulhhuN_31(i32 %a, i32 %b) {
; CHECK-LABEL: mulhhuN_31:
; CHECK: seal5.cv.mulhhun {{[^,]+}}, {{[^,]+}}, {{[^,]+}}, 31{{$}}
; CHECK: ret
  %1 = lshr i32 %a, 16
  %2 = lshr i32 %b, 16
  %3 = mul i32 %1, %2
  %4 = lshr i32 %3, 31
  ret i32 %4
}

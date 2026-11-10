; RUN: llc -O0 -mtriple=riscv32 -mattr=+m,+xcorevmac -verify-machineinstrs -global-isel=0 < %s | FileCheck %s
; RUN: llc -O3 -mtriple=riscv32 -mattr=+m,+xcorevmac -verify-machineinstrs -global-isel=0 < %s | FileCheck %s
; RUN: llc -O0 -mtriple=riscv32 -mattr=+m,+xcorevmac -verify-machineinstrs -global-isel=1 -global-isel-abort=1 < %s | FileCheck %s
; RUN: llc -O3 -mtriple=riscv32 -mattr=+m,+xcorevmac -verify-machineinstrs -global-isel=1 -global-isel-abort=1 < %s | FileCheck %s

define i32 @mulhhsN_1(i32 %a, i32 %b) {
; CHECK-LABEL: mulhhsN_1:
; CHECK: seal5.cv.mulhhsn {{[^,]+}}, {{[^,]+}}, {{[^,]+}}, 1{{$}}
; CHECK: ret
  %1 = ashr i32 %a, 16
  %2 = ashr i32 %b, 16
  %3 = mul i32 %1, %2
  %4 = ashr i32 %3, 1
  ret i32 %4
}

define i32 @mulhhsN_2(i32 %a, i32 %b) {
; CHECK-LABEL: mulhhsN_2:
; CHECK: seal5.cv.mulhhsn {{[^,]+}}, {{[^,]+}}, {{[^,]+}}, 2{{$}}
; CHECK: ret
  %1 = ashr i32 %a, 16
  %2 = ashr i32 %b, 16
  %3 = mul i32 %1, %2
  %4 = ashr i32 %3, 2
  ret i32 %4
}

define i32 @mulhhsN_3(i32 %a, i32 %b) {
; CHECK-LABEL: mulhhsN_3:
; CHECK: seal5.cv.mulhhsn {{[^,]+}}, {{[^,]+}}, {{[^,]+}}, 3{{$}}
; CHECK: ret
  %1 = ashr i32 %a, 16
  %2 = ashr i32 %b, 16
  %3 = mul i32 %1, %2
  %4 = ashr i32 %3, 3
  ret i32 %4
}

define i32 @mulhhsN_4(i32 %a, i32 %b) {
; CHECK-LABEL: mulhhsN_4:
; CHECK: seal5.cv.mulhhsn {{[^,]+}}, {{[^,]+}}, {{[^,]+}}, 4{{$}}
; CHECK: ret
  %1 = ashr i32 %a, 16
  %2 = ashr i32 %b, 16
  %3 = mul i32 %1, %2
  %4 = ashr i32 %3, 4
  ret i32 %4
}

define i32 @mulhhsN_5(i32 %a, i32 %b) {
; CHECK-LABEL: mulhhsN_5:
; CHECK: seal5.cv.mulhhsn {{[^,]+}}, {{[^,]+}}, {{[^,]+}}, 5{{$}}
; CHECK: ret
  %1 = ashr i32 %a, 16
  %2 = ashr i32 %b, 16
  %3 = mul i32 %1, %2
  %4 = ashr i32 %3, 5
  ret i32 %4
}

define i32 @mulhhsN_6(i32 %a, i32 %b) {
; CHECK-LABEL: mulhhsN_6:
; CHECK: seal5.cv.mulhhsn {{[^,]+}}, {{[^,]+}}, {{[^,]+}}, 6{{$}}
; CHECK: ret
  %1 = ashr i32 %a, 16
  %2 = ashr i32 %b, 16
  %3 = mul i32 %1, %2
  %4 = ashr i32 %3, 6
  ret i32 %4
}

define i32 @mulhhsN_7(i32 %a, i32 %b) {
; CHECK-LABEL: mulhhsN_7:
; CHECK: seal5.cv.mulhhsn {{[^,]+}}, {{[^,]+}}, {{[^,]+}}, 7{{$}}
; CHECK: ret
  %1 = ashr i32 %a, 16
  %2 = ashr i32 %b, 16
  %3 = mul i32 %1, %2
  %4 = ashr i32 %3, 7
  ret i32 %4
}

define i32 @mulhhsN_8(i32 %a, i32 %b) {
; CHECK-LABEL: mulhhsN_8:
; CHECK: seal5.cv.mulhhsn {{[^,]+}}, {{[^,]+}}, {{[^,]+}}, 8{{$}}
; CHECK: ret
  %1 = ashr i32 %a, 16
  %2 = ashr i32 %b, 16
  %3 = mul i32 %1, %2
  %4 = ashr i32 %3, 8
  ret i32 %4
}

define i32 @mulhhsN_9(i32 %a, i32 %b) {
; CHECK-LABEL: mulhhsN_9:
; CHECK: seal5.cv.mulhhsn {{[^,]+}}, {{[^,]+}}, {{[^,]+}}, 9{{$}}
; CHECK: ret
  %1 = ashr i32 %a, 16
  %2 = ashr i32 %b, 16
  %3 = mul i32 %1, %2
  %4 = ashr i32 %3, 9
  ret i32 %4
}

define i32 @mulhhsN_10(i32 %a, i32 %b) {
; CHECK-LABEL: mulhhsN_10:
; CHECK: seal5.cv.mulhhsn {{[^,]+}}, {{[^,]+}}, {{[^,]+}}, 10{{$}}
; CHECK: ret
  %1 = ashr i32 %a, 16
  %2 = ashr i32 %b, 16
  %3 = mul i32 %1, %2
  %4 = ashr i32 %3, 10
  ret i32 %4
}

define i32 @mulhhsN_11(i32 %a, i32 %b) {
; CHECK-LABEL: mulhhsN_11:
; CHECK: seal5.cv.mulhhsn {{[^,]+}}, {{[^,]+}}, {{[^,]+}}, 11{{$}}
; CHECK: ret
  %1 = ashr i32 %a, 16
  %2 = ashr i32 %b, 16
  %3 = mul i32 %1, %2
  %4 = ashr i32 %3, 11
  ret i32 %4
}

define i32 @mulhhsN_12(i32 %a, i32 %b) {
; CHECK-LABEL: mulhhsN_12:
; CHECK: seal5.cv.mulhhsn {{[^,]+}}, {{[^,]+}}, {{[^,]+}}, 12{{$}}
; CHECK: ret
  %1 = ashr i32 %a, 16
  %2 = ashr i32 %b, 16
  %3 = mul i32 %1, %2
  %4 = ashr i32 %3, 12
  ret i32 %4
}

define i32 @mulhhsN_13(i32 %a, i32 %b) {
; CHECK-LABEL: mulhhsN_13:
; CHECK: seal5.cv.mulhhsn {{[^,]+}}, {{[^,]+}}, {{[^,]+}}, 13{{$}}
; CHECK: ret
  %1 = ashr i32 %a, 16
  %2 = ashr i32 %b, 16
  %3 = mul i32 %1, %2
  %4 = ashr i32 %3, 13
  ret i32 %4
}

define i32 @mulhhsN_14(i32 %a, i32 %b) {
; CHECK-LABEL: mulhhsN_14:
; CHECK: seal5.cv.mulhhsn {{[^,]+}}, {{[^,]+}}, {{[^,]+}}, 14{{$}}
; CHECK: ret
  %1 = ashr i32 %a, 16
  %2 = ashr i32 %b, 16
  %3 = mul i32 %1, %2
  %4 = ashr i32 %3, 14
  ret i32 %4
}

define i32 @mulhhsN_15(i32 %a, i32 %b) {
; CHECK-LABEL: mulhhsN_15:
; CHECK: seal5.cv.mulhhsn {{[^,]+}}, {{[^,]+}}, {{[^,]+}}, 15{{$}}
; CHECK: ret
  %1 = ashr i32 %a, 16
  %2 = ashr i32 %b, 16
  %3 = mul i32 %1, %2
  %4 = ashr i32 %3, 15
  ret i32 %4
}

define i32 @mulhhsN_16(i32 %a, i32 %b) {
; CHECK-LABEL: mulhhsN_16:
; CHECK: seal5.cv.mulhhsn {{[^,]+}}, {{[^,]+}}, {{[^,]+}}, 16{{$}}
; CHECK: ret
  %1 = ashr i32 %a, 16
  %2 = ashr i32 %b, 16
  %3 = mul i32 %1, %2
  %4 = ashr i32 %3, 16
  ret i32 %4
}

define i32 @mulhhsN_17(i32 %a, i32 %b) {
; CHECK-LABEL: mulhhsN_17:
; CHECK: seal5.cv.mulhhsn {{[^,]+}}, {{[^,]+}}, {{[^,]+}}, 17{{$}}
; CHECK: ret
  %1 = ashr i32 %a, 16
  %2 = ashr i32 %b, 16
  %3 = mul i32 %1, %2
  %4 = ashr i32 %3, 17
  ret i32 %4
}

define i32 @mulhhsN_18(i32 %a, i32 %b) {
; CHECK-LABEL: mulhhsN_18:
; CHECK: seal5.cv.mulhhsn {{[^,]+}}, {{[^,]+}}, {{[^,]+}}, 18{{$}}
; CHECK: ret
  %1 = ashr i32 %a, 16
  %2 = ashr i32 %b, 16
  %3 = mul i32 %1, %2
  %4 = ashr i32 %3, 18
  ret i32 %4
}

define i32 @mulhhsN_19(i32 %a, i32 %b) {
; CHECK-LABEL: mulhhsN_19:
; CHECK: seal5.cv.mulhhsn {{[^,]+}}, {{[^,]+}}, {{[^,]+}}, 19{{$}}
; CHECK: ret
  %1 = ashr i32 %a, 16
  %2 = ashr i32 %b, 16
  %3 = mul i32 %1, %2
  %4 = ashr i32 %3, 19
  ret i32 %4
}

define i32 @mulhhsN_20(i32 %a, i32 %b) {
; CHECK-LABEL: mulhhsN_20:
; CHECK: seal5.cv.mulhhsn {{[^,]+}}, {{[^,]+}}, {{[^,]+}}, 20{{$}}
; CHECK: ret
  %1 = ashr i32 %a, 16
  %2 = ashr i32 %b, 16
  %3 = mul i32 %1, %2
  %4 = ashr i32 %3, 20
  ret i32 %4
}

define i32 @mulhhsN_21(i32 %a, i32 %b) {
; CHECK-LABEL: mulhhsN_21:
; CHECK: seal5.cv.mulhhsn {{[^,]+}}, {{[^,]+}}, {{[^,]+}}, 21{{$}}
; CHECK: ret
  %1 = ashr i32 %a, 16
  %2 = ashr i32 %b, 16
  %3 = mul i32 %1, %2
  %4 = ashr i32 %3, 21
  ret i32 %4
}

define i32 @mulhhsN_22(i32 %a, i32 %b) {
; CHECK-LABEL: mulhhsN_22:
; CHECK: seal5.cv.mulhhsn {{[^,]+}}, {{[^,]+}}, {{[^,]+}}, 22{{$}}
; CHECK: ret
  %1 = ashr i32 %a, 16
  %2 = ashr i32 %b, 16
  %3 = mul i32 %1, %2
  %4 = ashr i32 %3, 22
  ret i32 %4
}

define i32 @mulhhsN_23(i32 %a, i32 %b) {
; CHECK-LABEL: mulhhsN_23:
; CHECK: seal5.cv.mulhhsn {{[^,]+}}, {{[^,]+}}, {{[^,]+}}, 23{{$}}
; CHECK: ret
  %1 = ashr i32 %a, 16
  %2 = ashr i32 %b, 16
  %3 = mul i32 %1, %2
  %4 = ashr i32 %3, 23
  ret i32 %4
}

define i32 @mulhhsN_24(i32 %a, i32 %b) {
; CHECK-LABEL: mulhhsN_24:
; CHECK: seal5.cv.mulhhsn {{[^,]+}}, {{[^,]+}}, {{[^,]+}}, 24{{$}}
; CHECK: ret
  %1 = ashr i32 %a, 16
  %2 = ashr i32 %b, 16
  %3 = mul i32 %1, %2
  %4 = ashr i32 %3, 24
  ret i32 %4
}

define i32 @mulhhsN_25(i32 %a, i32 %b) {
; CHECK-LABEL: mulhhsN_25:
; CHECK: seal5.cv.mulhhsn {{[^,]+}}, {{[^,]+}}, {{[^,]+}}, 25{{$}}
; CHECK: ret
  %1 = ashr i32 %a, 16
  %2 = ashr i32 %b, 16
  %3 = mul i32 %1, %2
  %4 = ashr i32 %3, 25
  ret i32 %4
}

define i32 @mulhhsN_26(i32 %a, i32 %b) {
; CHECK-LABEL: mulhhsN_26:
; CHECK: seal5.cv.mulhhsn {{[^,]+}}, {{[^,]+}}, {{[^,]+}}, 26{{$}}
; CHECK: ret
  %1 = ashr i32 %a, 16
  %2 = ashr i32 %b, 16
  %3 = mul i32 %1, %2
  %4 = ashr i32 %3, 26
  ret i32 %4
}

define i32 @mulhhsN_27(i32 %a, i32 %b) {
; CHECK-LABEL: mulhhsN_27:
; CHECK: seal5.cv.mulhhsn {{[^,]+}}, {{[^,]+}}, {{[^,]+}}, 27{{$}}
; CHECK: ret
  %1 = ashr i32 %a, 16
  %2 = ashr i32 %b, 16
  %3 = mul i32 %1, %2
  %4 = ashr i32 %3, 27
  ret i32 %4
}

define i32 @mulhhsN_28(i32 %a, i32 %b) {
; CHECK-LABEL: mulhhsN_28:
; CHECK: seal5.cv.mulhhsn {{[^,]+}}, {{[^,]+}}, {{[^,]+}}, 28{{$}}
; CHECK: ret
  %1 = ashr i32 %a, 16
  %2 = ashr i32 %b, 16
  %3 = mul i32 %1, %2
  %4 = ashr i32 %3, 28
  ret i32 %4
}

define i32 @mulhhsN_29(i32 %a, i32 %b) {
; CHECK-LABEL: mulhhsN_29:
; CHECK: seal5.cv.mulhhsn {{[^,]+}}, {{[^,]+}}, {{[^,]+}}, 29{{$}}
; CHECK: ret
  %1 = ashr i32 %a, 16
  %2 = ashr i32 %b, 16
  %3 = mul i32 %1, %2
  %4 = ashr i32 %3, 29
  ret i32 %4
}

define i32 @mulhhsN_30(i32 %a, i32 %b) {
; CHECK-LABEL: mulhhsN_30:
; CHECK: seal5.cv.mulhhsn {{[^,]+}}, {{[^,]+}}, {{[^,]+}}, 30{{$}}
; CHECK: ret
  %1 = ashr i32 %a, 16
  %2 = ashr i32 %b, 16
  %3 = mul i32 %1, %2
  %4 = ashr i32 %3, 30
  ret i32 %4
}

define i32 @mulhhsN_31(i32 %a, i32 %b) {
; CHECK-LABEL: mulhhsN_31:
; CHECK: seal5.cv.mulhhsn {{[^,]+}}, {{[^,]+}}, {{[^,]+}}, 31{{$}}
; CHECK: ret
  %1 = ashr i32 %a, 16
  %2 = ashr i32 %b, 16
  %3 = mul i32 %1, %2
  %4 = ashr i32 %3, 31
  ret i32 %4
}

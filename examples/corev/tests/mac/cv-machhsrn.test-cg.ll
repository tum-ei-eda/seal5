; RUN: llc -O0 -mtriple=riscv32 -mattr=+m,+xcorevmac -verify-machineinstrs -global-isel=0 -global-isel-abort=1 < %s | FileCheck %s
; RUN: llc -O3 -mtriple=riscv32 -mattr=+m,+xcorevmac -verify-machineinstrs -global-isel=0 -global-isel-abort=1 < %s | FileCheck %s
; RUN: llc -O0 -mtriple=riscv32 -mattr=+m,+xcorevmac -verify-machineinstrs -global-isel=1 -global-isel-abort=1 < %s | FileCheck %s
; RUN: llc -O3 -mtriple=riscv32 -mattr=+m,+xcorevmac -verify-machineinstrs -global-isel=1 -global-isel-abort=1 < %s | FileCheck %s

define i32 @machhsrn_0(i32 %a, i32 %b, i32 %acc) {
; CHECK-LABEL: machhsrn_0:
; CHECK: seal5.cv.machhs{{r?}}n {{.*}}, 0{{$}}
; CHECK: ret
  %ahalf = ashr i32 %a, 16
  %bhalf = ashr i32 %b, 16
  %product = mul i32 %ahalf, %bhalf
  %accumulated = add i32 %product, %acc
  ret i32 %accumulated
}

define i32 @machhsrn_1(i32 %a, i32 %b, i32 %acc) {
; CHECK-LABEL: machhsrn_1:
; CHECK: seal5.cv.machhsrn {{.*}}, 1{{$}}
; CHECK: ret
  %ahalf = ashr i32 %a, 16
  %bhalf = ashr i32 %b, 16
  %product = mul i32 %ahalf, %bhalf
  %accumulated = add i32 %product, %acc
  %rounded = add i32 %accumulated, 1
  %result = ashr i32 %rounded, 1
  ret i32 %result
}

define i32 @machhsrn_2(i32 %a, i32 %b, i32 %acc) {
; CHECK-LABEL: machhsrn_2:
; CHECK: seal5.cv.machhsrn {{.*}}, 2{{$}}
; CHECK: ret
  %ahalf = ashr i32 %a, 16
  %bhalf = ashr i32 %b, 16
  %product = mul i32 %ahalf, %bhalf
  %accumulated = add i32 %product, %acc
  %rounded = add i32 %accumulated, 2
  %result = ashr i32 %rounded, 2
  ret i32 %result
}

define i32 @machhsrn_3(i32 %a, i32 %b, i32 %acc) {
; CHECK-LABEL: machhsrn_3:
; CHECK: seal5.cv.machhsrn {{.*}}, 3{{$}}
; CHECK: ret
  %ahalf = ashr i32 %a, 16
  %bhalf = ashr i32 %b, 16
  %product = mul i32 %ahalf, %bhalf
  %accumulated = add i32 %product, %acc
  %rounded = add i32 %accumulated, 4
  %result = ashr i32 %rounded, 3
  ret i32 %result
}

define i32 @machhsrn_4(i32 %a, i32 %b, i32 %acc) {
; CHECK-LABEL: machhsrn_4:
; CHECK: seal5.cv.machhsrn {{.*}}, 4{{$}}
; CHECK: ret
  %ahalf = ashr i32 %a, 16
  %bhalf = ashr i32 %b, 16
  %product = mul i32 %ahalf, %bhalf
  %accumulated = add i32 %product, %acc
  %rounded = add i32 %accumulated, 8
  %result = ashr i32 %rounded, 4
  ret i32 %result
}

define i32 @machhsrn_5(i32 %a, i32 %b, i32 %acc) {
; CHECK-LABEL: machhsrn_5:
; CHECK: seal5.cv.machhsrn {{.*}}, 5{{$}}
; CHECK: ret
  %ahalf = ashr i32 %a, 16
  %bhalf = ashr i32 %b, 16
  %product = mul i32 %ahalf, %bhalf
  %accumulated = add i32 %product, %acc
  %rounded = add i32 %accumulated, 16
  %result = ashr i32 %rounded, 5
  ret i32 %result
}

define i32 @machhsrn_6(i32 %a, i32 %b, i32 %acc) {
; CHECK-LABEL: machhsrn_6:
; CHECK: seal5.cv.machhsrn {{.*}}, 6{{$}}
; CHECK: ret
  %ahalf = ashr i32 %a, 16
  %bhalf = ashr i32 %b, 16
  %product = mul i32 %ahalf, %bhalf
  %accumulated = add i32 %product, %acc
  %rounded = add i32 %accumulated, 32
  %result = ashr i32 %rounded, 6
  ret i32 %result
}

define i32 @machhsrn_7(i32 %a, i32 %b, i32 %acc) {
; CHECK-LABEL: machhsrn_7:
; CHECK: seal5.cv.machhsrn {{.*}}, 7{{$}}
; CHECK: ret
  %ahalf = ashr i32 %a, 16
  %bhalf = ashr i32 %b, 16
  %product = mul i32 %ahalf, %bhalf
  %accumulated = add i32 %product, %acc
  %rounded = add i32 %accumulated, 64
  %result = ashr i32 %rounded, 7
  ret i32 %result
}

define i32 @machhsrn_8(i32 %a, i32 %b, i32 %acc) {
; CHECK-LABEL: machhsrn_8:
; CHECK: seal5.cv.machhsrn {{.*}}, 8{{$}}
; CHECK: ret
  %ahalf = ashr i32 %a, 16
  %bhalf = ashr i32 %b, 16
  %product = mul i32 %ahalf, %bhalf
  %accumulated = add i32 %product, %acc
  %rounded = add i32 %accumulated, 128
  %result = ashr i32 %rounded, 8
  ret i32 %result
}

define i32 @machhsrn_9(i32 %a, i32 %b, i32 %acc) {
; CHECK-LABEL: machhsrn_9:
; CHECK: seal5.cv.machhsrn {{.*}}, 9{{$}}
; CHECK: ret
  %ahalf = ashr i32 %a, 16
  %bhalf = ashr i32 %b, 16
  %product = mul i32 %ahalf, %bhalf
  %accumulated = add i32 %product, %acc
  %rounded = add i32 %accumulated, 256
  %result = ashr i32 %rounded, 9
  ret i32 %result
}

define i32 @machhsrn_10(i32 %a, i32 %b, i32 %acc) {
; CHECK-LABEL: machhsrn_10:
; CHECK: seal5.cv.machhsrn {{.*}}, 10{{$}}
; CHECK: ret
  %ahalf = ashr i32 %a, 16
  %bhalf = ashr i32 %b, 16
  %product = mul i32 %ahalf, %bhalf
  %accumulated = add i32 %product, %acc
  %rounded = add i32 %accumulated, 512
  %result = ashr i32 %rounded, 10
  ret i32 %result
}

define i32 @machhsrn_11(i32 %a, i32 %b, i32 %acc) {
; CHECK-LABEL: machhsrn_11:
; CHECK: seal5.cv.machhsrn {{.*}}, 11{{$}}
; CHECK: ret
  %ahalf = ashr i32 %a, 16
  %bhalf = ashr i32 %b, 16
  %product = mul i32 %ahalf, %bhalf
  %accumulated = add i32 %product, %acc
  %rounded = add i32 %accumulated, 1024
  %result = ashr i32 %rounded, 11
  ret i32 %result
}

define i32 @machhsrn_12(i32 %a, i32 %b, i32 %acc) {
; CHECK-LABEL: machhsrn_12:
; CHECK: seal5.cv.machhsrn {{.*}}, 12{{$}}
; CHECK: ret
  %ahalf = ashr i32 %a, 16
  %bhalf = ashr i32 %b, 16
  %product = mul i32 %ahalf, %bhalf
  %accumulated = add i32 %product, %acc
  %rounded = add i32 %accumulated, 2048
  %result = ashr i32 %rounded, 12
  ret i32 %result
}

define i32 @machhsrn_13(i32 %a, i32 %b, i32 %acc) {
; CHECK-LABEL: machhsrn_13:
; CHECK: seal5.cv.machhsrn {{.*}}, 13{{$}}
; CHECK: ret
  %ahalf = ashr i32 %a, 16
  %bhalf = ashr i32 %b, 16
  %product = mul i32 %ahalf, %bhalf
  %accumulated = add i32 %product, %acc
  %rounded = add i32 %accumulated, 4096
  %result = ashr i32 %rounded, 13
  ret i32 %result
}

define i32 @machhsrn_14(i32 %a, i32 %b, i32 %acc) {
; CHECK-LABEL: machhsrn_14:
; CHECK: seal5.cv.machhsrn {{.*}}, 14{{$}}
; CHECK: ret
  %ahalf = ashr i32 %a, 16
  %bhalf = ashr i32 %b, 16
  %product = mul i32 %ahalf, %bhalf
  %accumulated = add i32 %product, %acc
  %rounded = add i32 %accumulated, 8192
  %result = ashr i32 %rounded, 14
  ret i32 %result
}

define i32 @machhsrn_15(i32 %a, i32 %b, i32 %acc) {
; CHECK-LABEL: machhsrn_15:
; CHECK: seal5.cv.machhsrn {{.*}}, 15{{$}}
; CHECK: ret
  %ahalf = ashr i32 %a, 16
  %bhalf = ashr i32 %b, 16
  %product = mul i32 %ahalf, %bhalf
  %accumulated = add i32 %product, %acc
  %rounded = add i32 %accumulated, 16384
  %result = ashr i32 %rounded, 15
  ret i32 %result
}

define i32 @machhsrn_16(i32 %a, i32 %b, i32 %acc) {
; CHECK-LABEL: machhsrn_16:
; CHECK: seal5.cv.machhsrn {{.*}}, 16{{$}}
; CHECK: ret
  %ahalf = ashr i32 %a, 16
  %bhalf = ashr i32 %b, 16
  %product = mul i32 %ahalf, %bhalf
  %accumulated = add i32 %product, %acc
  %rounded = add i32 %accumulated, 32768
  %result = ashr i32 %rounded, 16
  ret i32 %result
}

define i32 @machhsrn_17(i32 %a, i32 %b, i32 %acc) {
; CHECK-LABEL: machhsrn_17:
; CHECK: seal5.cv.machhsrn {{.*}}, 17{{$}}
; CHECK: ret
  %ahalf = ashr i32 %a, 16
  %bhalf = ashr i32 %b, 16
  %product = mul i32 %ahalf, %bhalf
  %accumulated = add i32 %product, %acc
  %rounded = add i32 %accumulated, 65536
  %result = ashr i32 %rounded, 17
  ret i32 %result
}

define i32 @machhsrn_18(i32 %a, i32 %b, i32 %acc) {
; CHECK-LABEL: machhsrn_18:
; CHECK: seal5.cv.machhsrn {{.*}}, 18{{$}}
; CHECK: ret
  %ahalf = ashr i32 %a, 16
  %bhalf = ashr i32 %b, 16
  %product = mul i32 %ahalf, %bhalf
  %accumulated = add i32 %product, %acc
  %rounded = add i32 %accumulated, 131072
  %result = ashr i32 %rounded, 18
  ret i32 %result
}

define i32 @machhsrn_19(i32 %a, i32 %b, i32 %acc) {
; CHECK-LABEL: machhsrn_19:
; CHECK: seal5.cv.machhsrn {{.*}}, 19{{$}}
; CHECK: ret
  %ahalf = ashr i32 %a, 16
  %bhalf = ashr i32 %b, 16
  %product = mul i32 %ahalf, %bhalf
  %accumulated = add i32 %product, %acc
  %rounded = add i32 %accumulated, 262144
  %result = ashr i32 %rounded, 19
  ret i32 %result
}

define i32 @machhsrn_20(i32 %a, i32 %b, i32 %acc) {
; CHECK-LABEL: machhsrn_20:
; CHECK: seal5.cv.machhsrn {{.*}}, 20{{$}}
; CHECK: ret
  %ahalf = ashr i32 %a, 16
  %bhalf = ashr i32 %b, 16
  %product = mul i32 %ahalf, %bhalf
  %accumulated = add i32 %product, %acc
  %rounded = add i32 %accumulated, 524288
  %result = ashr i32 %rounded, 20
  ret i32 %result
}

define i32 @machhsrn_21(i32 %a, i32 %b, i32 %acc) {
; CHECK-LABEL: machhsrn_21:
; CHECK: seal5.cv.machhsrn {{.*}}, 21{{$}}
; CHECK: ret
  %ahalf = ashr i32 %a, 16
  %bhalf = ashr i32 %b, 16
  %product = mul i32 %ahalf, %bhalf
  %accumulated = add i32 %product, %acc
  %rounded = add i32 %accumulated, 1048576
  %result = ashr i32 %rounded, 21
  ret i32 %result
}

define i32 @machhsrn_22(i32 %a, i32 %b, i32 %acc) {
; CHECK-LABEL: machhsrn_22:
; CHECK: seal5.cv.machhsrn {{.*}}, 22{{$}}
; CHECK: ret
  %ahalf = ashr i32 %a, 16
  %bhalf = ashr i32 %b, 16
  %product = mul i32 %ahalf, %bhalf
  %accumulated = add i32 %product, %acc
  %rounded = add i32 %accumulated, 2097152
  %result = ashr i32 %rounded, 22
  ret i32 %result
}

define i32 @machhsrn_23(i32 %a, i32 %b, i32 %acc) {
; CHECK-LABEL: machhsrn_23:
; CHECK: seal5.cv.machhsrn {{.*}}, 23{{$}}
; CHECK: ret
  %ahalf = ashr i32 %a, 16
  %bhalf = ashr i32 %b, 16
  %product = mul i32 %ahalf, %bhalf
  %accumulated = add i32 %product, %acc
  %rounded = add i32 %accumulated, 4194304
  %result = ashr i32 %rounded, 23
  ret i32 %result
}

define i32 @machhsrn_24(i32 %a, i32 %b, i32 %acc) {
; CHECK-LABEL: machhsrn_24:
; CHECK: seal5.cv.machhsrn {{.*}}, 24{{$}}
; CHECK: ret
  %ahalf = ashr i32 %a, 16
  %bhalf = ashr i32 %b, 16
  %product = mul i32 %ahalf, %bhalf
  %accumulated = add i32 %product, %acc
  %rounded = add i32 %accumulated, 8388608
  %result = ashr i32 %rounded, 24
  ret i32 %result
}

define i32 @machhsrn_25(i32 %a, i32 %b, i32 %acc) {
; CHECK-LABEL: machhsrn_25:
; CHECK: seal5.cv.machhsrn {{.*}}, 25{{$}}
; CHECK: ret
  %ahalf = ashr i32 %a, 16
  %bhalf = ashr i32 %b, 16
  %product = mul i32 %ahalf, %bhalf
  %accumulated = add i32 %product, %acc
  %rounded = add i32 %accumulated, 16777216
  %result = ashr i32 %rounded, 25
  ret i32 %result
}

define i32 @machhsrn_26(i32 %a, i32 %b, i32 %acc) {
; CHECK-LABEL: machhsrn_26:
; CHECK: seal5.cv.machhsrn {{.*}}, 26{{$}}
; CHECK: ret
  %ahalf = ashr i32 %a, 16
  %bhalf = ashr i32 %b, 16
  %product = mul i32 %ahalf, %bhalf
  %accumulated = add i32 %product, %acc
  %rounded = add i32 %accumulated, 33554432
  %result = ashr i32 %rounded, 26
  ret i32 %result
}

define i32 @machhsrn_27(i32 %a, i32 %b, i32 %acc) {
; CHECK-LABEL: machhsrn_27:
; CHECK: seal5.cv.machhsrn {{.*}}, 27{{$}}
; CHECK: ret
  %ahalf = ashr i32 %a, 16
  %bhalf = ashr i32 %b, 16
  %product = mul i32 %ahalf, %bhalf
  %accumulated = add i32 %product, %acc
  %rounded = add i32 %accumulated, 67108864
  %result = ashr i32 %rounded, 27
  ret i32 %result
}

define i32 @machhsrn_28(i32 %a, i32 %b, i32 %acc) {
; CHECK-LABEL: machhsrn_28:
; CHECK: seal5.cv.machhsrn {{.*}}, 28{{$}}
; CHECK: ret
  %ahalf = ashr i32 %a, 16
  %bhalf = ashr i32 %b, 16
  %product = mul i32 %ahalf, %bhalf
  %accumulated = add i32 %product, %acc
  %rounded = add i32 %accumulated, 134217728
  %result = ashr i32 %rounded, 28
  ret i32 %result
}

define i32 @machhsrn_29(i32 %a, i32 %b, i32 %acc) {
; CHECK-LABEL: machhsrn_29:
; CHECK: seal5.cv.machhsrn {{.*}}, 29{{$}}
; CHECK: ret
  %ahalf = ashr i32 %a, 16
  %bhalf = ashr i32 %b, 16
  %product = mul i32 %ahalf, %bhalf
  %accumulated = add i32 %product, %acc
  %rounded = add i32 %accumulated, 268435456
  %result = ashr i32 %rounded, 29
  ret i32 %result
}

define i32 @machhsrn_30(i32 %a, i32 %b, i32 %acc) {
; CHECK-LABEL: machhsrn_30:
; CHECK: seal5.cv.machhsrn {{.*}}, 30{{$}}
; CHECK: ret
  %ahalf = ashr i32 %a, 16
  %bhalf = ashr i32 %b, 16
  %product = mul i32 %ahalf, %bhalf
  %accumulated = add i32 %product, %acc
  %rounded = add i32 %accumulated, 536870912
  %result = ashr i32 %rounded, 30
  ret i32 %result
}

define i32 @machhsrn_31(i32 %a, i32 %b, i32 %acc) {
; CHECK-LABEL: machhsrn_31:
; CHECK: seal5.cv.machhsrn {{.*}}, 31{{$}}
; CHECK: ret
  %ahalf = ashr i32 %a, 16
  %bhalf = ashr i32 %b, 16
  %product = mul i32 %ahalf, %bhalf
  %accumulated = add i32 %product, %acc
  %rounded = add i32 %accumulated, 1073741824
  %result = ashr i32 %rounded, 31
  ret i32 %result
}

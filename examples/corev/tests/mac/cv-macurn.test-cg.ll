; RUN: llc -O0 -mtriple=riscv32 -mattr=+m,+xcorevmac -verify-machineinstrs -global-isel=0 -global-isel-abort=1 < %s | FileCheck %s
; RUN: llc -O3 -mtriple=riscv32 -mattr=+m,+xcorevmac -verify-machineinstrs -global-isel=0 -global-isel-abort=1 < %s | FileCheck %s
; RUN: llc -O0 -mtriple=riscv32 -mattr=+m,+xcorevmac -verify-machineinstrs -global-isel=1 -global-isel-abort=1 < %s | FileCheck %s
; RUN: llc -O3 -mtriple=riscv32 -mattr=+m,+xcorevmac -verify-machineinstrs -global-isel=1 -global-isel-abort=1 < %s | FileCheck %s

define i32 @macurn_0(i32 %a, i32 %b, i32 %acc) {
; CHECK-LABEL: macurn_0:
; CHECK: seal5.cv.macu{{r?}}n {{.*}}, 0{{$}}
; CHECK: ret
  %ahalf = and i32 %a, 65535
  %bhalf = and i32 %b, 65535
  %product = mul i32 %ahalf, %bhalf
  %accumulated = add i32 %product, %acc
  ret i32 %accumulated
}

define i32 @macurn_1(i32 %a, i32 %b, i32 %acc) {
; CHECK-LABEL: macurn_1:
; CHECK: seal5.cv.macurn {{.*}}, 1{{$}}
; CHECK: ret
  %ahalf = and i32 %a, 65535
  %bhalf = and i32 %b, 65535
  %product = mul i32 %ahalf, %bhalf
  %accumulated = add i32 %product, %acc
  %rounded = add i32 %accumulated, 1
  %result = lshr i32 %rounded, 1
  ret i32 %result
}

define i32 @macurn_2(i32 %a, i32 %b, i32 %acc) {
; CHECK-LABEL: macurn_2:
; CHECK: seal5.cv.macurn {{.*}}, 2{{$}}
; CHECK: ret
  %ahalf = and i32 %a, 65535
  %bhalf = and i32 %b, 65535
  %product = mul i32 %ahalf, %bhalf
  %accumulated = add i32 %product, %acc
  %rounded = add i32 %accumulated, 2
  %result = lshr i32 %rounded, 2
  ret i32 %result
}

define i32 @macurn_3(i32 %a, i32 %b, i32 %acc) {
; CHECK-LABEL: macurn_3:
; CHECK: seal5.cv.macurn {{.*}}, 3{{$}}
; CHECK: ret
  %ahalf = and i32 %a, 65535
  %bhalf = and i32 %b, 65535
  %product = mul i32 %ahalf, %bhalf
  %accumulated = add i32 %product, %acc
  %rounded = add i32 %accumulated, 4
  %result = lshr i32 %rounded, 3
  ret i32 %result
}

define i32 @macurn_4(i32 %a, i32 %b, i32 %acc) {
; CHECK-LABEL: macurn_4:
; CHECK: seal5.cv.macurn {{.*}}, 4{{$}}
; CHECK: ret
  %ahalf = and i32 %a, 65535
  %bhalf = and i32 %b, 65535
  %product = mul i32 %ahalf, %bhalf
  %accumulated = add i32 %product, %acc
  %rounded = add i32 %accumulated, 8
  %result = lshr i32 %rounded, 4
  ret i32 %result
}

define i32 @macurn_5(i32 %a, i32 %b, i32 %acc) {
; CHECK-LABEL: macurn_5:
; CHECK: seal5.cv.macurn {{.*}}, 5{{$}}
; CHECK: ret
  %ahalf = and i32 %a, 65535
  %bhalf = and i32 %b, 65535
  %product = mul i32 %ahalf, %bhalf
  %accumulated = add i32 %product, %acc
  %rounded = add i32 %accumulated, 16
  %result = lshr i32 %rounded, 5
  ret i32 %result
}

define i32 @macurn_6(i32 %a, i32 %b, i32 %acc) {
; CHECK-LABEL: macurn_6:
; CHECK: seal5.cv.macurn {{.*}}, 6{{$}}
; CHECK: ret
  %ahalf = and i32 %a, 65535
  %bhalf = and i32 %b, 65535
  %product = mul i32 %ahalf, %bhalf
  %accumulated = add i32 %product, %acc
  %rounded = add i32 %accumulated, 32
  %result = lshr i32 %rounded, 6
  ret i32 %result
}

define i32 @macurn_7(i32 %a, i32 %b, i32 %acc) {
; CHECK-LABEL: macurn_7:
; CHECK: seal5.cv.macurn {{.*}}, 7{{$}}
; CHECK: ret
  %ahalf = and i32 %a, 65535
  %bhalf = and i32 %b, 65535
  %product = mul i32 %ahalf, %bhalf
  %accumulated = add i32 %product, %acc
  %rounded = add i32 %accumulated, 64
  %result = lshr i32 %rounded, 7
  ret i32 %result
}

define i32 @macurn_8(i32 %a, i32 %b, i32 %acc) {
; CHECK-LABEL: macurn_8:
; CHECK: seal5.cv.macurn {{.*}}, 8{{$}}
; CHECK: ret
  %ahalf = and i32 %a, 65535
  %bhalf = and i32 %b, 65535
  %product = mul i32 %ahalf, %bhalf
  %accumulated = add i32 %product, %acc
  %rounded = add i32 %accumulated, 128
  %result = lshr i32 %rounded, 8
  ret i32 %result
}

define i32 @macurn_9(i32 %a, i32 %b, i32 %acc) {
; CHECK-LABEL: macurn_9:
; CHECK: seal5.cv.macurn {{.*}}, 9{{$}}
; CHECK: ret
  %ahalf = and i32 %a, 65535
  %bhalf = and i32 %b, 65535
  %product = mul i32 %ahalf, %bhalf
  %accumulated = add i32 %product, %acc
  %rounded = add i32 %accumulated, 256
  %result = lshr i32 %rounded, 9
  ret i32 %result
}

define i32 @macurn_10(i32 %a, i32 %b, i32 %acc) {
; CHECK-LABEL: macurn_10:
; CHECK: seal5.cv.macurn {{.*}}, 10{{$}}
; CHECK: ret
  %ahalf = and i32 %a, 65535
  %bhalf = and i32 %b, 65535
  %product = mul i32 %ahalf, %bhalf
  %accumulated = add i32 %product, %acc
  %rounded = add i32 %accumulated, 512
  %result = lshr i32 %rounded, 10
  ret i32 %result
}

define i32 @macurn_11(i32 %a, i32 %b, i32 %acc) {
; CHECK-LABEL: macurn_11:
; CHECK: seal5.cv.macurn {{.*}}, 11{{$}}
; CHECK: ret
  %ahalf = and i32 %a, 65535
  %bhalf = and i32 %b, 65535
  %product = mul i32 %ahalf, %bhalf
  %accumulated = add i32 %product, %acc
  %rounded = add i32 %accumulated, 1024
  %result = lshr i32 %rounded, 11
  ret i32 %result
}

define i32 @macurn_12(i32 %a, i32 %b, i32 %acc) {
; CHECK-LABEL: macurn_12:
; CHECK: seal5.cv.macurn {{.*}}, 12{{$}}
; CHECK: ret
  %ahalf = and i32 %a, 65535
  %bhalf = and i32 %b, 65535
  %product = mul i32 %ahalf, %bhalf
  %accumulated = add i32 %product, %acc
  %rounded = add i32 %accumulated, 2048
  %result = lshr i32 %rounded, 12
  ret i32 %result
}

define i32 @macurn_13(i32 %a, i32 %b, i32 %acc) {
; CHECK-LABEL: macurn_13:
; CHECK: seal5.cv.macurn {{.*}}, 13{{$}}
; CHECK: ret
  %ahalf = and i32 %a, 65535
  %bhalf = and i32 %b, 65535
  %product = mul i32 %ahalf, %bhalf
  %accumulated = add i32 %product, %acc
  %rounded = add i32 %accumulated, 4096
  %result = lshr i32 %rounded, 13
  ret i32 %result
}

define i32 @macurn_14(i32 %a, i32 %b, i32 %acc) {
; CHECK-LABEL: macurn_14:
; CHECK: seal5.cv.macurn {{.*}}, 14{{$}}
; CHECK: ret
  %ahalf = and i32 %a, 65535
  %bhalf = and i32 %b, 65535
  %product = mul i32 %ahalf, %bhalf
  %accumulated = add i32 %product, %acc
  %rounded = add i32 %accumulated, 8192
  %result = lshr i32 %rounded, 14
  ret i32 %result
}

define i32 @macurn_15(i32 %a, i32 %b, i32 %acc) {
; CHECK-LABEL: macurn_15:
; CHECK: seal5.cv.macurn {{.*}}, 15{{$}}
; CHECK: ret
  %ahalf = and i32 %a, 65535
  %bhalf = and i32 %b, 65535
  %product = mul i32 %ahalf, %bhalf
  %accumulated = add i32 %product, %acc
  %rounded = add i32 %accumulated, 16384
  %result = lshr i32 %rounded, 15
  ret i32 %result
}

define i32 @macurn_16(i32 %a, i32 %b, i32 %acc) {
; CHECK-LABEL: macurn_16:
; CHECK: seal5.cv.macurn {{.*}}, 16{{$}}
; CHECK: ret
  %ahalf = and i32 %a, 65535
  %bhalf = and i32 %b, 65535
  %product = mul i32 %ahalf, %bhalf
  %accumulated = add i32 %product, %acc
  %rounded = add i32 %accumulated, 32768
  %result = lshr i32 %rounded, 16
  ret i32 %result
}

define i32 @macurn_17(i32 %a, i32 %b, i32 %acc) {
; CHECK-LABEL: macurn_17:
; CHECK: seal5.cv.macurn {{.*}}, 17{{$}}
; CHECK: ret
  %ahalf = and i32 %a, 65535
  %bhalf = and i32 %b, 65535
  %product = mul i32 %ahalf, %bhalf
  %accumulated = add i32 %product, %acc
  %rounded = add i32 %accumulated, 65536
  %result = lshr i32 %rounded, 17
  ret i32 %result
}

define i32 @macurn_18(i32 %a, i32 %b, i32 %acc) {
; CHECK-LABEL: macurn_18:
; CHECK: seal5.cv.macurn {{.*}}, 18{{$}}
; CHECK: ret
  %ahalf = and i32 %a, 65535
  %bhalf = and i32 %b, 65535
  %product = mul i32 %ahalf, %bhalf
  %accumulated = add i32 %product, %acc
  %rounded = add i32 %accumulated, 131072
  %result = lshr i32 %rounded, 18
  ret i32 %result
}

define i32 @macurn_19(i32 %a, i32 %b, i32 %acc) {
; CHECK-LABEL: macurn_19:
; CHECK: seal5.cv.macurn {{.*}}, 19{{$}}
; CHECK: ret
  %ahalf = and i32 %a, 65535
  %bhalf = and i32 %b, 65535
  %product = mul i32 %ahalf, %bhalf
  %accumulated = add i32 %product, %acc
  %rounded = add i32 %accumulated, 262144
  %result = lshr i32 %rounded, 19
  ret i32 %result
}

define i32 @macurn_20(i32 %a, i32 %b, i32 %acc) {
; CHECK-LABEL: macurn_20:
; CHECK: seal5.cv.macurn {{.*}}, 20{{$}}
; CHECK: ret
  %ahalf = and i32 %a, 65535
  %bhalf = and i32 %b, 65535
  %product = mul i32 %ahalf, %bhalf
  %accumulated = add i32 %product, %acc
  %rounded = add i32 %accumulated, 524288
  %result = lshr i32 %rounded, 20
  ret i32 %result
}

define i32 @macurn_21(i32 %a, i32 %b, i32 %acc) {
; CHECK-LABEL: macurn_21:
; CHECK: seal5.cv.macurn {{.*}}, 21{{$}}
; CHECK: ret
  %ahalf = and i32 %a, 65535
  %bhalf = and i32 %b, 65535
  %product = mul i32 %ahalf, %bhalf
  %accumulated = add i32 %product, %acc
  %rounded = add i32 %accumulated, 1048576
  %result = lshr i32 %rounded, 21
  ret i32 %result
}

define i32 @macurn_22(i32 %a, i32 %b, i32 %acc) {
; CHECK-LABEL: macurn_22:
; CHECK: seal5.cv.macurn {{.*}}, 22{{$}}
; CHECK: ret
  %ahalf = and i32 %a, 65535
  %bhalf = and i32 %b, 65535
  %product = mul i32 %ahalf, %bhalf
  %accumulated = add i32 %product, %acc
  %rounded = add i32 %accumulated, 2097152
  %result = lshr i32 %rounded, 22
  ret i32 %result
}

define i32 @macurn_23(i32 %a, i32 %b, i32 %acc) {
; CHECK-LABEL: macurn_23:
; CHECK: seal5.cv.macurn {{.*}}, 23{{$}}
; CHECK: ret
  %ahalf = and i32 %a, 65535
  %bhalf = and i32 %b, 65535
  %product = mul i32 %ahalf, %bhalf
  %accumulated = add i32 %product, %acc
  %rounded = add i32 %accumulated, 4194304
  %result = lshr i32 %rounded, 23
  ret i32 %result
}

define i32 @macurn_24(i32 %a, i32 %b, i32 %acc) {
; CHECK-LABEL: macurn_24:
; CHECK: seal5.cv.macurn {{.*}}, 24{{$}}
; CHECK: ret
  %ahalf = and i32 %a, 65535
  %bhalf = and i32 %b, 65535
  %product = mul i32 %ahalf, %bhalf
  %accumulated = add i32 %product, %acc
  %rounded = add i32 %accumulated, 8388608
  %result = lshr i32 %rounded, 24
  ret i32 %result
}

define i32 @macurn_25(i32 %a, i32 %b, i32 %acc) {
; CHECK-LABEL: macurn_25:
; CHECK: seal5.cv.macurn {{.*}}, 25{{$}}
; CHECK: ret
  %ahalf = and i32 %a, 65535
  %bhalf = and i32 %b, 65535
  %product = mul i32 %ahalf, %bhalf
  %accumulated = add i32 %product, %acc
  %rounded = add i32 %accumulated, 16777216
  %result = lshr i32 %rounded, 25
  ret i32 %result
}

define i32 @macurn_26(i32 %a, i32 %b, i32 %acc) {
; CHECK-LABEL: macurn_26:
; CHECK: seal5.cv.macurn {{.*}}, 26{{$}}
; CHECK: ret
  %ahalf = and i32 %a, 65535
  %bhalf = and i32 %b, 65535
  %product = mul i32 %ahalf, %bhalf
  %accumulated = add i32 %product, %acc
  %rounded = add i32 %accumulated, 33554432
  %result = lshr i32 %rounded, 26
  ret i32 %result
}

define i32 @macurn_27(i32 %a, i32 %b, i32 %acc) {
; CHECK-LABEL: macurn_27:
; CHECK: seal5.cv.macurn {{.*}}, 27{{$}}
; CHECK: ret
  %ahalf = and i32 %a, 65535
  %bhalf = and i32 %b, 65535
  %product = mul i32 %ahalf, %bhalf
  %accumulated = add i32 %product, %acc
  %rounded = add i32 %accumulated, 67108864
  %result = lshr i32 %rounded, 27
  ret i32 %result
}

define i32 @macurn_28(i32 %a, i32 %b, i32 %acc) {
; CHECK-LABEL: macurn_28:
; CHECK: seal5.cv.macurn {{.*}}, 28{{$}}
; CHECK: ret
  %ahalf = and i32 %a, 65535
  %bhalf = and i32 %b, 65535
  %product = mul i32 %ahalf, %bhalf
  %accumulated = add i32 %product, %acc
  %rounded = add i32 %accumulated, 134217728
  %result = lshr i32 %rounded, 28
  ret i32 %result
}

define i32 @macurn_29(i32 %a, i32 %b, i32 %acc) {
; CHECK-LABEL: macurn_29:
; CHECK: seal5.cv.macurn {{.*}}, 29{{$}}
; CHECK: ret
  %ahalf = and i32 %a, 65535
  %bhalf = and i32 %b, 65535
  %product = mul i32 %ahalf, %bhalf
  %accumulated = add i32 %product, %acc
  %rounded = add i32 %accumulated, 268435456
  %result = lshr i32 %rounded, 29
  ret i32 %result
}

define i32 @macurn_30(i32 %a, i32 %b, i32 %acc) {
; CHECK-LABEL: macurn_30:
; CHECK: seal5.cv.macurn {{.*}}, 30{{$}}
; CHECK: ret
  %ahalf = and i32 %a, 65535
  %bhalf = and i32 %b, 65535
  %product = mul i32 %ahalf, %bhalf
  %accumulated = add i32 %product, %acc
  %rounded = add i32 %accumulated, 536870912
  %result = lshr i32 %rounded, 30
  ret i32 %result
}

define i32 @macurn_31(i32 %a, i32 %b, i32 %acc) {
; CHECK-LABEL: macurn_31:
; CHECK: seal5.cv.macurn {{.*}}, 31{{$}}
; CHECK: ret
  %ahalf = and i32 %a, 65535
  %bhalf = and i32 %b, 65535
  %product = mul i32 %ahalf, %bhalf
  %accumulated = add i32 %product, %acc
  %rounded = add i32 %accumulated, 1073741824
  %result = lshr i32 %rounded, 31
  ret i32 %result
}

; RUN: llc -O0 -mtriple=riscv32 -mattr=+m,+xcorevmac -verify-machineinstrs -global-isel=0 -global-isel-abort=1 < %s | FileCheck %s
; RUN: llc -O3 -mtriple=riscv32 -mattr=+m,+xcorevmac -verify-machineinstrs -global-isel=0 -global-isel-abort=1 < %s | FileCheck %s
; RUN: llc -O0 -mtriple=riscv32 -mattr=+m,+xcorevmac -verify-machineinstrs -global-isel=1 -global-isel-abort=1 < %s | FileCheck %s
; RUN: llc -O3 -mtriple=riscv32 -mattr=+m,+xcorevmac -verify-machineinstrs -global-isel=1 -global-isel-abort=1 < %s | FileCheck %s

define i32 @machhurn_0(i32 %a, i32 %b, i32 %acc) {
; CHECK-LABEL: machhurn_0:
; CHECK: seal5.cv.machhu{{r?}}n {{.*}}, 0{{$}}
; CHECK: ret
  %ahalf = lshr i32 %a, 16
  %bhalf = lshr i32 %b, 16
  %product = mul i32 %ahalf, %bhalf
  %accumulated = add i32 %product, %acc
  ret i32 %accumulated
}

define i32 @machhurn_1(i32 %a, i32 %b, i32 %acc) {
; CHECK-LABEL: machhurn_1:
; CHECK: seal5.cv.machhurn {{.*}}, 1{{$}}
; CHECK: ret
  %ahalf = lshr i32 %a, 16
  %bhalf = lshr i32 %b, 16
  %product = mul i32 %ahalf, %bhalf
  %accumulated = add i32 %product, %acc
  %rounded = add i32 %accumulated, 1
  %result = lshr i32 %rounded, 1
  ret i32 %result
}

define i32 @machhurn_2(i32 %a, i32 %b, i32 %acc) {
; CHECK-LABEL: machhurn_2:
; CHECK: seal5.cv.machhurn {{.*}}, 2{{$}}
; CHECK: ret
  %ahalf = lshr i32 %a, 16
  %bhalf = lshr i32 %b, 16
  %product = mul i32 %ahalf, %bhalf
  %accumulated = add i32 %product, %acc
  %rounded = add i32 %accumulated, 2
  %result = lshr i32 %rounded, 2
  ret i32 %result
}

define i32 @machhurn_3(i32 %a, i32 %b, i32 %acc) {
; CHECK-LABEL: machhurn_3:
; CHECK: seal5.cv.machhurn {{.*}}, 3{{$}}
; CHECK: ret
  %ahalf = lshr i32 %a, 16
  %bhalf = lshr i32 %b, 16
  %product = mul i32 %ahalf, %bhalf
  %accumulated = add i32 %product, %acc
  %rounded = add i32 %accumulated, 4
  %result = lshr i32 %rounded, 3
  ret i32 %result
}

define i32 @machhurn_4(i32 %a, i32 %b, i32 %acc) {
; CHECK-LABEL: machhurn_4:
; CHECK: seal5.cv.machhurn {{.*}}, 4{{$}}
; CHECK: ret
  %ahalf = lshr i32 %a, 16
  %bhalf = lshr i32 %b, 16
  %product = mul i32 %ahalf, %bhalf
  %accumulated = add i32 %product, %acc
  %rounded = add i32 %accumulated, 8
  %result = lshr i32 %rounded, 4
  ret i32 %result
}

define i32 @machhurn_5(i32 %a, i32 %b, i32 %acc) {
; CHECK-LABEL: machhurn_5:
; CHECK: seal5.cv.machhurn {{.*}}, 5{{$}}
; CHECK: ret
  %ahalf = lshr i32 %a, 16
  %bhalf = lshr i32 %b, 16
  %product = mul i32 %ahalf, %bhalf
  %accumulated = add i32 %product, %acc
  %rounded = add i32 %accumulated, 16
  %result = lshr i32 %rounded, 5
  ret i32 %result
}

define i32 @machhurn_6(i32 %a, i32 %b, i32 %acc) {
; CHECK-LABEL: machhurn_6:
; CHECK: seal5.cv.machhurn {{.*}}, 6{{$}}
; CHECK: ret
  %ahalf = lshr i32 %a, 16
  %bhalf = lshr i32 %b, 16
  %product = mul i32 %ahalf, %bhalf
  %accumulated = add i32 %product, %acc
  %rounded = add i32 %accumulated, 32
  %result = lshr i32 %rounded, 6
  ret i32 %result
}

define i32 @machhurn_7(i32 %a, i32 %b, i32 %acc) {
; CHECK-LABEL: machhurn_7:
; CHECK: seal5.cv.machhurn {{.*}}, 7{{$}}
; CHECK: ret
  %ahalf = lshr i32 %a, 16
  %bhalf = lshr i32 %b, 16
  %product = mul i32 %ahalf, %bhalf
  %accumulated = add i32 %product, %acc
  %rounded = add i32 %accumulated, 64
  %result = lshr i32 %rounded, 7
  ret i32 %result
}

define i32 @machhurn_8(i32 %a, i32 %b, i32 %acc) {
; CHECK-LABEL: machhurn_8:
; CHECK: seal5.cv.machhurn {{.*}}, 8{{$}}
; CHECK: ret
  %ahalf = lshr i32 %a, 16
  %bhalf = lshr i32 %b, 16
  %product = mul i32 %ahalf, %bhalf
  %accumulated = add i32 %product, %acc
  %rounded = add i32 %accumulated, 128
  %result = lshr i32 %rounded, 8
  ret i32 %result
}

define i32 @machhurn_9(i32 %a, i32 %b, i32 %acc) {
; CHECK-LABEL: machhurn_9:
; CHECK: seal5.cv.machhurn {{.*}}, 9{{$}}
; CHECK: ret
  %ahalf = lshr i32 %a, 16
  %bhalf = lshr i32 %b, 16
  %product = mul i32 %ahalf, %bhalf
  %accumulated = add i32 %product, %acc
  %rounded = add i32 %accumulated, 256
  %result = lshr i32 %rounded, 9
  ret i32 %result
}

define i32 @machhurn_10(i32 %a, i32 %b, i32 %acc) {
; CHECK-LABEL: machhurn_10:
; CHECK: seal5.cv.machhurn {{.*}}, 10{{$}}
; CHECK: ret
  %ahalf = lshr i32 %a, 16
  %bhalf = lshr i32 %b, 16
  %product = mul i32 %ahalf, %bhalf
  %accumulated = add i32 %product, %acc
  %rounded = add i32 %accumulated, 512
  %result = lshr i32 %rounded, 10
  ret i32 %result
}

define i32 @machhurn_11(i32 %a, i32 %b, i32 %acc) {
; CHECK-LABEL: machhurn_11:
; CHECK: seal5.cv.machhurn {{.*}}, 11{{$}}
; CHECK: ret
  %ahalf = lshr i32 %a, 16
  %bhalf = lshr i32 %b, 16
  %product = mul i32 %ahalf, %bhalf
  %accumulated = add i32 %product, %acc
  %rounded = add i32 %accumulated, 1024
  %result = lshr i32 %rounded, 11
  ret i32 %result
}

define i32 @machhurn_12(i32 %a, i32 %b, i32 %acc) {
; CHECK-LABEL: machhurn_12:
; CHECK: seal5.cv.machhurn {{.*}}, 12{{$}}
; CHECK: ret
  %ahalf = lshr i32 %a, 16
  %bhalf = lshr i32 %b, 16
  %product = mul i32 %ahalf, %bhalf
  %accumulated = add i32 %product, %acc
  %rounded = add i32 %accumulated, 2048
  %result = lshr i32 %rounded, 12
  ret i32 %result
}

define i32 @machhurn_13(i32 %a, i32 %b, i32 %acc) {
; CHECK-LABEL: machhurn_13:
; CHECK: seal5.cv.machhurn {{.*}}, 13{{$}}
; CHECK: ret
  %ahalf = lshr i32 %a, 16
  %bhalf = lshr i32 %b, 16
  %product = mul i32 %ahalf, %bhalf
  %accumulated = add i32 %product, %acc
  %rounded = add i32 %accumulated, 4096
  %result = lshr i32 %rounded, 13
  ret i32 %result
}

define i32 @machhurn_14(i32 %a, i32 %b, i32 %acc) {
; CHECK-LABEL: machhurn_14:
; CHECK: seal5.cv.machhurn {{.*}}, 14{{$}}
; CHECK: ret
  %ahalf = lshr i32 %a, 16
  %bhalf = lshr i32 %b, 16
  %product = mul i32 %ahalf, %bhalf
  %accumulated = add i32 %product, %acc
  %rounded = add i32 %accumulated, 8192
  %result = lshr i32 %rounded, 14
  ret i32 %result
}

define i32 @machhurn_15(i32 %a, i32 %b, i32 %acc) {
; CHECK-LABEL: machhurn_15:
; CHECK: seal5.cv.machhurn {{.*}}, 15{{$}}
; CHECK: ret
  %ahalf = lshr i32 %a, 16
  %bhalf = lshr i32 %b, 16
  %product = mul i32 %ahalf, %bhalf
  %accumulated = add i32 %product, %acc
  %rounded = add i32 %accumulated, 16384
  %result = lshr i32 %rounded, 15
  ret i32 %result
}

define i32 @machhurn_16(i32 %a, i32 %b, i32 %acc) {
; CHECK-LABEL: machhurn_16:
; CHECK: seal5.cv.machhurn {{.*}}, 16{{$}}
; CHECK: ret
  %ahalf = lshr i32 %a, 16
  %bhalf = lshr i32 %b, 16
  %product = mul i32 %ahalf, %bhalf
  %accumulated = add i32 %product, %acc
  %rounded = add i32 %accumulated, 32768
  %result = lshr i32 %rounded, 16
  ret i32 %result
}

define i32 @machhurn_17(i32 %a, i32 %b, i32 %acc) {
; CHECK-LABEL: machhurn_17:
; CHECK: seal5.cv.machhurn {{.*}}, 17{{$}}
; CHECK: ret
  %ahalf = lshr i32 %a, 16
  %bhalf = lshr i32 %b, 16
  %product = mul i32 %ahalf, %bhalf
  %accumulated = add i32 %product, %acc
  %rounded = add i32 %accumulated, 65536
  %result = lshr i32 %rounded, 17
  ret i32 %result
}

define i32 @machhurn_18(i32 %a, i32 %b, i32 %acc) {
; CHECK-LABEL: machhurn_18:
; CHECK: seal5.cv.machhurn {{.*}}, 18{{$}}
; CHECK: ret
  %ahalf = lshr i32 %a, 16
  %bhalf = lshr i32 %b, 16
  %product = mul i32 %ahalf, %bhalf
  %accumulated = add i32 %product, %acc
  %rounded = add i32 %accumulated, 131072
  %result = lshr i32 %rounded, 18
  ret i32 %result
}

define i32 @machhurn_19(i32 %a, i32 %b, i32 %acc) {
; CHECK-LABEL: machhurn_19:
; CHECK: seal5.cv.machhurn {{.*}}, 19{{$}}
; CHECK: ret
  %ahalf = lshr i32 %a, 16
  %bhalf = lshr i32 %b, 16
  %product = mul i32 %ahalf, %bhalf
  %accumulated = add i32 %product, %acc
  %rounded = add i32 %accumulated, 262144
  %result = lshr i32 %rounded, 19
  ret i32 %result
}

define i32 @machhurn_20(i32 %a, i32 %b, i32 %acc) {
; CHECK-LABEL: machhurn_20:
; CHECK: seal5.cv.machhurn {{.*}}, 20{{$}}
; CHECK: ret
  %ahalf = lshr i32 %a, 16
  %bhalf = lshr i32 %b, 16
  %product = mul i32 %ahalf, %bhalf
  %accumulated = add i32 %product, %acc
  %rounded = add i32 %accumulated, 524288
  %result = lshr i32 %rounded, 20
  ret i32 %result
}

define i32 @machhurn_21(i32 %a, i32 %b, i32 %acc) {
; CHECK-LABEL: machhurn_21:
; CHECK: seal5.cv.machhurn {{.*}}, 21{{$}}
; CHECK: ret
  %ahalf = lshr i32 %a, 16
  %bhalf = lshr i32 %b, 16
  %product = mul i32 %ahalf, %bhalf
  %accumulated = add i32 %product, %acc
  %rounded = add i32 %accumulated, 1048576
  %result = lshr i32 %rounded, 21
  ret i32 %result
}

define i32 @machhurn_22(i32 %a, i32 %b, i32 %acc) {
; CHECK-LABEL: machhurn_22:
; CHECK: seal5.cv.machhurn {{.*}}, 22{{$}}
; CHECK: ret
  %ahalf = lshr i32 %a, 16
  %bhalf = lshr i32 %b, 16
  %product = mul i32 %ahalf, %bhalf
  %accumulated = add i32 %product, %acc
  %rounded = add i32 %accumulated, 2097152
  %result = lshr i32 %rounded, 22
  ret i32 %result
}

define i32 @machhurn_23(i32 %a, i32 %b, i32 %acc) {
; CHECK-LABEL: machhurn_23:
; CHECK: seal5.cv.machhurn {{.*}}, 23{{$}}
; CHECK: ret
  %ahalf = lshr i32 %a, 16
  %bhalf = lshr i32 %b, 16
  %product = mul i32 %ahalf, %bhalf
  %accumulated = add i32 %product, %acc
  %rounded = add i32 %accumulated, 4194304
  %result = lshr i32 %rounded, 23
  ret i32 %result
}

define i32 @machhurn_24(i32 %a, i32 %b, i32 %acc) {
; CHECK-LABEL: machhurn_24:
; CHECK: seal5.cv.machhurn {{.*}}, 24{{$}}
; CHECK: ret
  %ahalf = lshr i32 %a, 16
  %bhalf = lshr i32 %b, 16
  %product = mul i32 %ahalf, %bhalf
  %accumulated = add i32 %product, %acc
  %rounded = add i32 %accumulated, 8388608
  %result = lshr i32 %rounded, 24
  ret i32 %result
}

define i32 @machhurn_25(i32 %a, i32 %b, i32 %acc) {
; CHECK-LABEL: machhurn_25:
; CHECK: seal5.cv.machhurn {{.*}}, 25{{$}}
; CHECK: ret
  %ahalf = lshr i32 %a, 16
  %bhalf = lshr i32 %b, 16
  %product = mul i32 %ahalf, %bhalf
  %accumulated = add i32 %product, %acc
  %rounded = add i32 %accumulated, 16777216
  %result = lshr i32 %rounded, 25
  ret i32 %result
}

define i32 @machhurn_26(i32 %a, i32 %b, i32 %acc) {
; CHECK-LABEL: machhurn_26:
; CHECK: seal5.cv.machhurn {{.*}}, 26{{$}}
; CHECK: ret
  %ahalf = lshr i32 %a, 16
  %bhalf = lshr i32 %b, 16
  %product = mul i32 %ahalf, %bhalf
  %accumulated = add i32 %product, %acc
  %rounded = add i32 %accumulated, 33554432
  %result = lshr i32 %rounded, 26
  ret i32 %result
}

define i32 @machhurn_27(i32 %a, i32 %b, i32 %acc) {
; CHECK-LABEL: machhurn_27:
; CHECK: seal5.cv.machhurn {{.*}}, 27{{$}}
; CHECK: ret
  %ahalf = lshr i32 %a, 16
  %bhalf = lshr i32 %b, 16
  %product = mul i32 %ahalf, %bhalf
  %accumulated = add i32 %product, %acc
  %rounded = add i32 %accumulated, 67108864
  %result = lshr i32 %rounded, 27
  ret i32 %result
}

define i32 @machhurn_28(i32 %a, i32 %b, i32 %acc) {
; CHECK-LABEL: machhurn_28:
; CHECK: seal5.cv.machhurn {{.*}}, 28{{$}}
; CHECK: ret
  %ahalf = lshr i32 %a, 16
  %bhalf = lshr i32 %b, 16
  %product = mul i32 %ahalf, %bhalf
  %accumulated = add i32 %product, %acc
  %rounded = add i32 %accumulated, 134217728
  %result = lshr i32 %rounded, 28
  ret i32 %result
}

define i32 @machhurn_29(i32 %a, i32 %b, i32 %acc) {
; CHECK-LABEL: machhurn_29:
; CHECK: seal5.cv.machhurn {{.*}}, 29{{$}}
; CHECK: ret
  %ahalf = lshr i32 %a, 16
  %bhalf = lshr i32 %b, 16
  %product = mul i32 %ahalf, %bhalf
  %accumulated = add i32 %product, %acc
  %rounded = add i32 %accumulated, 268435456
  %result = lshr i32 %rounded, 29
  ret i32 %result
}

define i32 @machhurn_30(i32 %a, i32 %b, i32 %acc) {
; CHECK-LABEL: machhurn_30:
; CHECK: seal5.cv.machhurn {{.*}}, 30{{$}}
; CHECK: ret
  %ahalf = lshr i32 %a, 16
  %bhalf = lshr i32 %b, 16
  %product = mul i32 %ahalf, %bhalf
  %accumulated = add i32 %product, %acc
  %rounded = add i32 %accumulated, 536870912
  %result = lshr i32 %rounded, 30
  ret i32 %result
}

define i32 @machhurn_31(i32 %a, i32 %b, i32 %acc) {
; CHECK-LABEL: machhurn_31:
; CHECK: seal5.cv.machhurn {{.*}}, 31{{$}}
; CHECK: ret
  %ahalf = lshr i32 %a, 16
  %bhalf = lshr i32 %b, 16
  %product = mul i32 %ahalf, %bhalf
  %accumulated = add i32 %product, %acc
  %rounded = add i32 %accumulated, 1073741824
  %result = lshr i32 %rounded, 31
  ret i32 %result
}

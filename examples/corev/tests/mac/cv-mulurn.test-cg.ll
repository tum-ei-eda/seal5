; RUN: llc -O0 -mtriple=riscv32 -mattr=+m,+xcorevmac -verify-machineinstrs -global-isel=0 -global-isel-abort=1 < %s | FileCheck %s
; RUN: llc -O3 -mtriple=riscv32 -mattr=+m,+xcorevmac -verify-machineinstrs -global-isel=0 -global-isel-abort=1 < %s | FileCheck %s
; RUN: llc -O0 -mtriple=riscv32 -mattr=+m,+xcorevmac -verify-machineinstrs -global-isel=1 -global-isel-abort=1 < %s | FileCheck %s
; RUN: llc -O3 -mtriple=riscv32 -mattr=+m,+xcorevmac -verify-machineinstrs -global-isel=1 -global-isel-abort=1 < %s | FileCheck %s

define i32 @mulurn_0(i32 %a, i32 %b) {
; CHECK-LABEL: mulurn_0:
; CHECK: seal5.cv.mulu{{r?}}n {{.*}}, 0{{$}}
; CHECK: ret
  %ahalf = and i32 %a, 65535
  %bhalf = and i32 %b, 65535
  %product = mul i32 %ahalf, %bhalf
  ret i32 %product
}

define i32 @mulurn_1(i32 %a, i32 %b) {
; CHECK-LABEL: mulurn_1:
; CHECK: seal5.cv.mulurn {{.*}}, 1{{$}}
; CHECK: ret
  %ahalf = and i32 %a, 65535
  %bhalf = and i32 %b, 65535
  %product = mul i32 %ahalf, %bhalf
  %rounded = add i32 %product, 1
  %result = lshr i32 %rounded, 1
  ret i32 %result
}

define i32 @mulurn_2(i32 %a, i32 %b) {
; CHECK-LABEL: mulurn_2:
; CHECK: seal5.cv.mulurn {{.*}}, 2{{$}}
; CHECK: ret
  %ahalf = and i32 %a, 65535
  %bhalf = and i32 %b, 65535
  %product = mul i32 %ahalf, %bhalf
  %rounded = add i32 %product, 2
  %result = lshr i32 %rounded, 2
  ret i32 %result
}

define i32 @mulurn_3(i32 %a, i32 %b) {
; CHECK-LABEL: mulurn_3:
; CHECK: seal5.cv.mulurn {{.*}}, 3{{$}}
; CHECK: ret
  %ahalf = and i32 %a, 65535
  %bhalf = and i32 %b, 65535
  %product = mul i32 %ahalf, %bhalf
  %rounded = add i32 %product, 4
  %result = lshr i32 %rounded, 3
  ret i32 %result
}

define i32 @mulurn_4(i32 %a, i32 %b) {
; CHECK-LABEL: mulurn_4:
; CHECK: seal5.cv.mulurn {{.*}}, 4{{$}}
; CHECK: ret
  %ahalf = and i32 %a, 65535
  %bhalf = and i32 %b, 65535
  %product = mul i32 %ahalf, %bhalf
  %rounded = add i32 %product, 8
  %result = lshr i32 %rounded, 4
  ret i32 %result
}

define i32 @mulurn_5(i32 %a, i32 %b) {
; CHECK-LABEL: mulurn_5:
; CHECK: seal5.cv.mulurn {{.*}}, 5{{$}}
; CHECK: ret
  %ahalf = and i32 %a, 65535
  %bhalf = and i32 %b, 65535
  %product = mul i32 %ahalf, %bhalf
  %rounded = add i32 %product, 16
  %result = lshr i32 %rounded, 5
  ret i32 %result
}

define i32 @mulurn_6(i32 %a, i32 %b) {
; CHECK-LABEL: mulurn_6:
; CHECK: seal5.cv.mulurn {{.*}}, 6{{$}}
; CHECK: ret
  %ahalf = and i32 %a, 65535
  %bhalf = and i32 %b, 65535
  %product = mul i32 %ahalf, %bhalf
  %rounded = add i32 %product, 32
  %result = lshr i32 %rounded, 6
  ret i32 %result
}

define i32 @mulurn_7(i32 %a, i32 %b) {
; CHECK-LABEL: mulurn_7:
; CHECK: seal5.cv.mulurn {{.*}}, 7{{$}}
; CHECK: ret
  %ahalf = and i32 %a, 65535
  %bhalf = and i32 %b, 65535
  %product = mul i32 %ahalf, %bhalf
  %rounded = add i32 %product, 64
  %result = lshr i32 %rounded, 7
  ret i32 %result
}

define i32 @mulurn_8(i32 %a, i32 %b) {
; CHECK-LABEL: mulurn_8:
; CHECK: seal5.cv.mulurn {{.*}}, 8{{$}}
; CHECK: ret
  %ahalf = and i32 %a, 65535
  %bhalf = and i32 %b, 65535
  %product = mul i32 %ahalf, %bhalf
  %rounded = add i32 %product, 128
  %result = lshr i32 %rounded, 8
  ret i32 %result
}

define i32 @mulurn_9(i32 %a, i32 %b) {
; CHECK-LABEL: mulurn_9:
; CHECK: seal5.cv.mulurn {{.*}}, 9{{$}}
; CHECK: ret
  %ahalf = and i32 %a, 65535
  %bhalf = and i32 %b, 65535
  %product = mul i32 %ahalf, %bhalf
  %rounded = add i32 %product, 256
  %result = lshr i32 %rounded, 9
  ret i32 %result
}

define i32 @mulurn_10(i32 %a, i32 %b) {
; CHECK-LABEL: mulurn_10:
; CHECK: seal5.cv.mulurn {{.*}}, 10{{$}}
; CHECK: ret
  %ahalf = and i32 %a, 65535
  %bhalf = and i32 %b, 65535
  %product = mul i32 %ahalf, %bhalf
  %rounded = add i32 %product, 512
  %result = lshr i32 %rounded, 10
  ret i32 %result
}

define i32 @mulurn_11(i32 %a, i32 %b) {
; CHECK-LABEL: mulurn_11:
; CHECK: seal5.cv.mulurn {{.*}}, 11{{$}}
; CHECK: ret
  %ahalf = and i32 %a, 65535
  %bhalf = and i32 %b, 65535
  %product = mul i32 %ahalf, %bhalf
  %rounded = add i32 %product, 1024
  %result = lshr i32 %rounded, 11
  ret i32 %result
}

define i32 @mulurn_12(i32 %a, i32 %b) {
; CHECK-LABEL: mulurn_12:
; CHECK: seal5.cv.mulurn {{.*}}, 12{{$}}
; CHECK: ret
  %ahalf = and i32 %a, 65535
  %bhalf = and i32 %b, 65535
  %product = mul i32 %ahalf, %bhalf
  %rounded = add i32 %product, 2048
  %result = lshr i32 %rounded, 12
  ret i32 %result
}

define i32 @mulurn_13(i32 %a, i32 %b) {
; CHECK-LABEL: mulurn_13:
; CHECK: seal5.cv.mulurn {{.*}}, 13{{$}}
; CHECK: ret
  %ahalf = and i32 %a, 65535
  %bhalf = and i32 %b, 65535
  %product = mul i32 %ahalf, %bhalf
  %rounded = add i32 %product, 4096
  %result = lshr i32 %rounded, 13
  ret i32 %result
}

define i32 @mulurn_14(i32 %a, i32 %b) {
; CHECK-LABEL: mulurn_14:
; CHECK: seal5.cv.mulurn {{.*}}, 14{{$}}
; CHECK: ret
  %ahalf = and i32 %a, 65535
  %bhalf = and i32 %b, 65535
  %product = mul i32 %ahalf, %bhalf
  %rounded = add i32 %product, 8192
  %result = lshr i32 %rounded, 14
  ret i32 %result
}

define i32 @mulurn_15(i32 %a, i32 %b) {
; CHECK-LABEL: mulurn_15:
; CHECK: seal5.cv.mulurn {{.*}}, 15{{$}}
; CHECK: ret
  %ahalf = and i32 %a, 65535
  %bhalf = and i32 %b, 65535
  %product = mul i32 %ahalf, %bhalf
  %rounded = add i32 %product, 16384
  %result = lshr i32 %rounded, 15
  ret i32 %result
}

define i32 @mulurn_16(i32 %a, i32 %b) {
; CHECK-LABEL: mulurn_16:
; CHECK: seal5.cv.mulurn {{.*}}, 16{{$}}
; CHECK: ret
  %ahalf = and i32 %a, 65535
  %bhalf = and i32 %b, 65535
  %product = mul i32 %ahalf, %bhalf
  %rounded = add i32 %product, 32768
  %result = lshr i32 %rounded, 16
  ret i32 %result
}

define i32 @mulurn_17(i32 %a, i32 %b) {
; CHECK-LABEL: mulurn_17:
; CHECK: seal5.cv.mulurn {{.*}}, 17{{$}}
; CHECK: ret
  %ahalf = and i32 %a, 65535
  %bhalf = and i32 %b, 65535
  %product = mul i32 %ahalf, %bhalf
  %rounded = add i32 %product, 65536
  %result = lshr i32 %rounded, 17
  ret i32 %result
}

define i32 @mulurn_18(i32 %a, i32 %b) {
; CHECK-LABEL: mulurn_18:
; CHECK: seal5.cv.mulurn {{.*}}, 18{{$}}
; CHECK: ret
  %ahalf = and i32 %a, 65535
  %bhalf = and i32 %b, 65535
  %product = mul i32 %ahalf, %bhalf
  %rounded = add i32 %product, 131072
  %result = lshr i32 %rounded, 18
  ret i32 %result
}

define i32 @mulurn_19(i32 %a, i32 %b) {
; CHECK-LABEL: mulurn_19:
; CHECK: seal5.cv.mulurn {{.*}}, 19{{$}}
; CHECK: ret
  %ahalf = and i32 %a, 65535
  %bhalf = and i32 %b, 65535
  %product = mul i32 %ahalf, %bhalf
  %rounded = add i32 %product, 262144
  %result = lshr i32 %rounded, 19
  ret i32 %result
}

define i32 @mulurn_20(i32 %a, i32 %b) {
; CHECK-LABEL: mulurn_20:
; CHECK: seal5.cv.mulurn {{.*}}, 20{{$}}
; CHECK: ret
  %ahalf = and i32 %a, 65535
  %bhalf = and i32 %b, 65535
  %product = mul i32 %ahalf, %bhalf
  %rounded = add i32 %product, 524288
  %result = lshr i32 %rounded, 20
  ret i32 %result
}

define i32 @mulurn_21(i32 %a, i32 %b) {
; CHECK-LABEL: mulurn_21:
; CHECK: seal5.cv.mulurn {{.*}}, 21{{$}}
; CHECK: ret
  %ahalf = and i32 %a, 65535
  %bhalf = and i32 %b, 65535
  %product = mul i32 %ahalf, %bhalf
  %rounded = add i32 %product, 1048576
  %result = lshr i32 %rounded, 21
  ret i32 %result
}

define i32 @mulurn_22(i32 %a, i32 %b) {
; CHECK-LABEL: mulurn_22:
; CHECK: seal5.cv.mulurn {{.*}}, 22{{$}}
; CHECK: ret
  %ahalf = and i32 %a, 65535
  %bhalf = and i32 %b, 65535
  %product = mul i32 %ahalf, %bhalf
  %rounded = add i32 %product, 2097152
  %result = lshr i32 %rounded, 22
  ret i32 %result
}

define i32 @mulurn_23(i32 %a, i32 %b) {
; CHECK-LABEL: mulurn_23:
; CHECK: seal5.cv.mulurn {{.*}}, 23{{$}}
; CHECK: ret
  %ahalf = and i32 %a, 65535
  %bhalf = and i32 %b, 65535
  %product = mul i32 %ahalf, %bhalf
  %rounded = add i32 %product, 4194304
  %result = lshr i32 %rounded, 23
  ret i32 %result
}

define i32 @mulurn_24(i32 %a, i32 %b) {
; CHECK-LABEL: mulurn_24:
; CHECK: seal5.cv.mulurn {{.*}}, 24{{$}}
; CHECK: ret
  %ahalf = and i32 %a, 65535
  %bhalf = and i32 %b, 65535
  %product = mul i32 %ahalf, %bhalf
  %rounded = add i32 %product, 8388608
  %result = lshr i32 %rounded, 24
  ret i32 %result
}

define i32 @mulurn_25(i32 %a, i32 %b) {
; CHECK-LABEL: mulurn_25:
; CHECK: seal5.cv.mulurn {{.*}}, 25{{$}}
; CHECK: ret
  %ahalf = and i32 %a, 65535
  %bhalf = and i32 %b, 65535
  %product = mul i32 %ahalf, %bhalf
  %rounded = add i32 %product, 16777216
  %result = lshr i32 %rounded, 25
  ret i32 %result
}

define i32 @mulurn_26(i32 %a, i32 %b) {
; CHECK-LABEL: mulurn_26:
; CHECK: seal5.cv.mulurn {{.*}}, 26{{$}}
; CHECK: ret
  %ahalf = and i32 %a, 65535
  %bhalf = and i32 %b, 65535
  %product = mul i32 %ahalf, %bhalf
  %rounded = add i32 %product, 33554432
  %result = lshr i32 %rounded, 26
  ret i32 %result
}

define i32 @mulurn_27(i32 %a, i32 %b) {
; CHECK-LABEL: mulurn_27:
; CHECK: seal5.cv.mulurn {{.*}}, 27{{$}}
; CHECK: ret
  %ahalf = and i32 %a, 65535
  %bhalf = and i32 %b, 65535
  %product = mul i32 %ahalf, %bhalf
  %rounded = add i32 %product, 67108864
  %result = lshr i32 %rounded, 27
  ret i32 %result
}

define i32 @mulurn_28(i32 %a, i32 %b) {
; CHECK-LABEL: mulurn_28:
; CHECK: seal5.cv.mulurn {{.*}}, 28{{$}}
; CHECK: ret
  %ahalf = and i32 %a, 65535
  %bhalf = and i32 %b, 65535
  %product = mul i32 %ahalf, %bhalf
  %rounded = add i32 %product, 134217728
  %result = lshr i32 %rounded, 28
  ret i32 %result
}

define i32 @mulurn_29(i32 %a, i32 %b) {
; CHECK-LABEL: mulurn_29:
; CHECK: seal5.cv.mulurn {{.*}}, 29{{$}}
; CHECK: ret
  %ahalf = and i32 %a, 65535
  %bhalf = and i32 %b, 65535
  %product = mul i32 %ahalf, %bhalf
  %rounded = add i32 %product, 268435456
  %result = lshr i32 %rounded, 29
  ret i32 %result
}

define i32 @mulurn_30(i32 %a, i32 %b) {
; CHECK-LABEL: mulurn_30:
; CHECK: seal5.cv.mulurn {{.*}}, 30{{$}}
; CHECK: ret
  %ahalf = and i32 %a, 65535
  %bhalf = and i32 %b, 65535
  %product = mul i32 %ahalf, %bhalf
  %rounded = add i32 %product, 536870912
  %result = lshr i32 %rounded, 30
  ret i32 %result
}

define i32 @mulurn_31(i32 %a, i32 %b) {
; CHECK-LABEL: mulurn_31:
; CHECK: seal5.cv.mulurn {{.*}}, 31{{$}}
; CHECK: ret
  %ahalf = and i32 %a, 65535
  %bhalf = and i32 %b, 65535
  %product = mul i32 %ahalf, %bhalf
  %rounded = add i32 %product, 1073741824
  %result = lshr i32 %rounded, 31
  ret i32 %result
}

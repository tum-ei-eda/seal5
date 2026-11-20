; RUN: llc -O0 -mtriple=riscv32 -mattr=+m,+xcorevmac -verify-machineinstrs -global-isel=0 -global-isel-abort=1 < %s | FileCheck %s
; RUN: llc -O3 -mtriple=riscv32 -mattr=+m,+xcorevmac -verify-machineinstrs -global-isel=0 -global-isel-abort=1 < %s | FileCheck %s
; RUN: llc -O0 -mtriple=riscv32 -mattr=+m,+xcorevmac -verify-machineinstrs -global-isel=1 -global-isel-abort=1 < %s | FileCheck %s
; RUN: llc -O3 -mtriple=riscv32 -mattr=+m,+xcorevmac -verify-machineinstrs -global-isel=1 -global-isel-abort=1 < %s | FileCheck %s

define i32 @mulhhurn_0(i32 %a, i32 %b) {
; CHECK-LABEL: mulhhurn_0:
; CHECK: seal5.cv.mulhhu{{r?}}n {{.*}}, 0{{$}}
; CHECK: ret
  %ahalf = lshr i32 %a, 16
  %bhalf = lshr i32 %b, 16
  %product = mul i32 %ahalf, %bhalf
  ret i32 %product
}

define i32 @mulhhurn_1(i32 %a, i32 %b) {
; CHECK-LABEL: mulhhurn_1:
; CHECK: seal5.cv.mulhhurn {{.*}}, 1{{$}}
; CHECK: ret
  %ahalf = lshr i32 %a, 16
  %bhalf = lshr i32 %b, 16
  %product = mul i32 %ahalf, %bhalf
  %rounded = add i32 %product, 1
  %result = lshr i32 %rounded, 1
  ret i32 %result
}

define i32 @mulhhurn_2(i32 %a, i32 %b) {
; CHECK-LABEL: mulhhurn_2:
; CHECK: seal5.cv.mulhhurn {{.*}}, 2{{$}}
; CHECK: ret
  %ahalf = lshr i32 %a, 16
  %bhalf = lshr i32 %b, 16
  %product = mul i32 %ahalf, %bhalf
  %rounded = add i32 %product, 2
  %result = lshr i32 %rounded, 2
  ret i32 %result
}

define i32 @mulhhurn_3(i32 %a, i32 %b) {
; CHECK-LABEL: mulhhurn_3:
; CHECK: seal5.cv.mulhhurn {{.*}}, 3{{$}}
; CHECK: ret
  %ahalf = lshr i32 %a, 16
  %bhalf = lshr i32 %b, 16
  %product = mul i32 %ahalf, %bhalf
  %rounded = add i32 %product, 4
  %result = lshr i32 %rounded, 3
  ret i32 %result
}

define i32 @mulhhurn_4(i32 %a, i32 %b) {
; CHECK-LABEL: mulhhurn_4:
; CHECK: seal5.cv.mulhhurn {{.*}}, 4{{$}}
; CHECK: ret
  %ahalf = lshr i32 %a, 16
  %bhalf = lshr i32 %b, 16
  %product = mul i32 %ahalf, %bhalf
  %rounded = add i32 %product, 8
  %result = lshr i32 %rounded, 4
  ret i32 %result
}

define i32 @mulhhurn_5(i32 %a, i32 %b) {
; CHECK-LABEL: mulhhurn_5:
; CHECK: seal5.cv.mulhhurn {{.*}}, 5{{$}}
; CHECK: ret
  %ahalf = lshr i32 %a, 16
  %bhalf = lshr i32 %b, 16
  %product = mul i32 %ahalf, %bhalf
  %rounded = add i32 %product, 16
  %result = lshr i32 %rounded, 5
  ret i32 %result
}

define i32 @mulhhurn_6(i32 %a, i32 %b) {
; CHECK-LABEL: mulhhurn_6:
; CHECK: seal5.cv.mulhhurn {{.*}}, 6{{$}}
; CHECK: ret
  %ahalf = lshr i32 %a, 16
  %bhalf = lshr i32 %b, 16
  %product = mul i32 %ahalf, %bhalf
  %rounded = add i32 %product, 32
  %result = lshr i32 %rounded, 6
  ret i32 %result
}

define i32 @mulhhurn_7(i32 %a, i32 %b) {
; CHECK-LABEL: mulhhurn_7:
; CHECK: seal5.cv.mulhhurn {{.*}}, 7{{$}}
; CHECK: ret
  %ahalf = lshr i32 %a, 16
  %bhalf = lshr i32 %b, 16
  %product = mul i32 %ahalf, %bhalf
  %rounded = add i32 %product, 64
  %result = lshr i32 %rounded, 7
  ret i32 %result
}

define i32 @mulhhurn_8(i32 %a, i32 %b) {
; CHECK-LABEL: mulhhurn_8:
; CHECK: seal5.cv.mulhhurn {{.*}}, 8{{$}}
; CHECK: ret
  %ahalf = lshr i32 %a, 16
  %bhalf = lshr i32 %b, 16
  %product = mul i32 %ahalf, %bhalf
  %rounded = add i32 %product, 128
  %result = lshr i32 %rounded, 8
  ret i32 %result
}

define i32 @mulhhurn_9(i32 %a, i32 %b) {
; CHECK-LABEL: mulhhurn_9:
; CHECK: seal5.cv.mulhhurn {{.*}}, 9{{$}}
; CHECK: ret
  %ahalf = lshr i32 %a, 16
  %bhalf = lshr i32 %b, 16
  %product = mul i32 %ahalf, %bhalf
  %rounded = add i32 %product, 256
  %result = lshr i32 %rounded, 9
  ret i32 %result
}

define i32 @mulhhurn_10(i32 %a, i32 %b) {
; CHECK-LABEL: mulhhurn_10:
; CHECK: seal5.cv.mulhhurn {{.*}}, 10{{$}}
; CHECK: ret
  %ahalf = lshr i32 %a, 16
  %bhalf = lshr i32 %b, 16
  %product = mul i32 %ahalf, %bhalf
  %rounded = add i32 %product, 512
  %result = lshr i32 %rounded, 10
  ret i32 %result
}

define i32 @mulhhurn_11(i32 %a, i32 %b) {
; CHECK-LABEL: mulhhurn_11:
; CHECK: seal5.cv.mulhhurn {{.*}}, 11{{$}}
; CHECK: ret
  %ahalf = lshr i32 %a, 16
  %bhalf = lshr i32 %b, 16
  %product = mul i32 %ahalf, %bhalf
  %rounded = add i32 %product, 1024
  %result = lshr i32 %rounded, 11
  ret i32 %result
}

define i32 @mulhhurn_12(i32 %a, i32 %b) {
; CHECK-LABEL: mulhhurn_12:
; CHECK: seal5.cv.mulhhurn {{.*}}, 12{{$}}
; CHECK: ret
  %ahalf = lshr i32 %a, 16
  %bhalf = lshr i32 %b, 16
  %product = mul i32 %ahalf, %bhalf
  %rounded = add i32 %product, 2048
  %result = lshr i32 %rounded, 12
  ret i32 %result
}

define i32 @mulhhurn_13(i32 %a, i32 %b) {
; CHECK-LABEL: mulhhurn_13:
; CHECK: seal5.cv.mulhhurn {{.*}}, 13{{$}}
; CHECK: ret
  %ahalf = lshr i32 %a, 16
  %bhalf = lshr i32 %b, 16
  %product = mul i32 %ahalf, %bhalf
  %rounded = add i32 %product, 4096
  %result = lshr i32 %rounded, 13
  ret i32 %result
}

define i32 @mulhhurn_14(i32 %a, i32 %b) {
; CHECK-LABEL: mulhhurn_14:
; CHECK: seal5.cv.mulhhurn {{.*}}, 14{{$}}
; CHECK: ret
  %ahalf = lshr i32 %a, 16
  %bhalf = lshr i32 %b, 16
  %product = mul i32 %ahalf, %bhalf
  %rounded = add i32 %product, 8192
  %result = lshr i32 %rounded, 14
  ret i32 %result
}

define i32 @mulhhurn_15(i32 %a, i32 %b) {
; CHECK-LABEL: mulhhurn_15:
; CHECK: seal5.cv.mulhhurn {{.*}}, 15{{$}}
; CHECK: ret
  %ahalf = lshr i32 %a, 16
  %bhalf = lshr i32 %b, 16
  %product = mul i32 %ahalf, %bhalf
  %rounded = add i32 %product, 16384
  %result = lshr i32 %rounded, 15
  ret i32 %result
}

define i32 @mulhhurn_16(i32 %a, i32 %b) {
; CHECK-LABEL: mulhhurn_16:
; CHECK: seal5.cv.mulhhurn {{.*}}, 16{{$}}
; CHECK: ret
  %ahalf = lshr i32 %a, 16
  %bhalf = lshr i32 %b, 16
  %product = mul i32 %ahalf, %bhalf
  %rounded = add i32 %product, 32768
  %result = lshr i32 %rounded, 16
  ret i32 %result
}

define i32 @mulhhurn_17(i32 %a, i32 %b) {
; CHECK-LABEL: mulhhurn_17:
; CHECK: seal5.cv.mulhhurn {{.*}}, 17{{$}}
; CHECK: ret
  %ahalf = lshr i32 %a, 16
  %bhalf = lshr i32 %b, 16
  %product = mul i32 %ahalf, %bhalf
  %rounded = add i32 %product, 65536
  %result = lshr i32 %rounded, 17
  ret i32 %result
}

define i32 @mulhhurn_18(i32 %a, i32 %b) {
; CHECK-LABEL: mulhhurn_18:
; CHECK: seal5.cv.mulhhurn {{.*}}, 18{{$}}
; CHECK: ret
  %ahalf = lshr i32 %a, 16
  %bhalf = lshr i32 %b, 16
  %product = mul i32 %ahalf, %bhalf
  %rounded = add i32 %product, 131072
  %result = lshr i32 %rounded, 18
  ret i32 %result
}

define i32 @mulhhurn_19(i32 %a, i32 %b) {
; CHECK-LABEL: mulhhurn_19:
; CHECK: seal5.cv.mulhhurn {{.*}}, 19{{$}}
; CHECK: ret
  %ahalf = lshr i32 %a, 16
  %bhalf = lshr i32 %b, 16
  %product = mul i32 %ahalf, %bhalf
  %rounded = add i32 %product, 262144
  %result = lshr i32 %rounded, 19
  ret i32 %result
}

define i32 @mulhhurn_20(i32 %a, i32 %b) {
; CHECK-LABEL: mulhhurn_20:
; CHECK: seal5.cv.mulhhurn {{.*}}, 20{{$}}
; CHECK: ret
  %ahalf = lshr i32 %a, 16
  %bhalf = lshr i32 %b, 16
  %product = mul i32 %ahalf, %bhalf
  %rounded = add i32 %product, 524288
  %result = lshr i32 %rounded, 20
  ret i32 %result
}

define i32 @mulhhurn_21(i32 %a, i32 %b) {
; CHECK-LABEL: mulhhurn_21:
; CHECK: seal5.cv.mulhhurn {{.*}}, 21{{$}}
; CHECK: ret
  %ahalf = lshr i32 %a, 16
  %bhalf = lshr i32 %b, 16
  %product = mul i32 %ahalf, %bhalf
  %rounded = add i32 %product, 1048576
  %result = lshr i32 %rounded, 21
  ret i32 %result
}

define i32 @mulhhurn_22(i32 %a, i32 %b) {
; CHECK-LABEL: mulhhurn_22:
; CHECK: seal5.cv.mulhhurn {{.*}}, 22{{$}}
; CHECK: ret
  %ahalf = lshr i32 %a, 16
  %bhalf = lshr i32 %b, 16
  %product = mul i32 %ahalf, %bhalf
  %rounded = add i32 %product, 2097152
  %result = lshr i32 %rounded, 22
  ret i32 %result
}

define i32 @mulhhurn_23(i32 %a, i32 %b) {
; CHECK-LABEL: mulhhurn_23:
; CHECK: seal5.cv.mulhhurn {{.*}}, 23{{$}}
; CHECK: ret
  %ahalf = lshr i32 %a, 16
  %bhalf = lshr i32 %b, 16
  %product = mul i32 %ahalf, %bhalf
  %rounded = add i32 %product, 4194304
  %result = lshr i32 %rounded, 23
  ret i32 %result
}

define i32 @mulhhurn_24(i32 %a, i32 %b) {
; CHECK-LABEL: mulhhurn_24:
; CHECK: seal5.cv.mulhhurn {{.*}}, 24{{$}}
; CHECK: ret
  %ahalf = lshr i32 %a, 16
  %bhalf = lshr i32 %b, 16
  %product = mul i32 %ahalf, %bhalf
  %rounded = add i32 %product, 8388608
  %result = lshr i32 %rounded, 24
  ret i32 %result
}

define i32 @mulhhurn_25(i32 %a, i32 %b) {
; CHECK-LABEL: mulhhurn_25:
; CHECK: seal5.cv.mulhhurn {{.*}}, 25{{$}}
; CHECK: ret
  %ahalf = lshr i32 %a, 16
  %bhalf = lshr i32 %b, 16
  %product = mul i32 %ahalf, %bhalf
  %rounded = add i32 %product, 16777216
  %result = lshr i32 %rounded, 25
  ret i32 %result
}

define i32 @mulhhurn_26(i32 %a, i32 %b) {
; CHECK-LABEL: mulhhurn_26:
; CHECK: seal5.cv.mulhhurn {{.*}}, 26{{$}}
; CHECK: ret
  %ahalf = lshr i32 %a, 16
  %bhalf = lshr i32 %b, 16
  %product = mul i32 %ahalf, %bhalf
  %rounded = add i32 %product, 33554432
  %result = lshr i32 %rounded, 26
  ret i32 %result
}

define i32 @mulhhurn_27(i32 %a, i32 %b) {
; CHECK-LABEL: mulhhurn_27:
; CHECK: seal5.cv.mulhhurn {{.*}}, 27{{$}}
; CHECK: ret
  %ahalf = lshr i32 %a, 16
  %bhalf = lshr i32 %b, 16
  %product = mul i32 %ahalf, %bhalf
  %rounded = add i32 %product, 67108864
  %result = lshr i32 %rounded, 27
  ret i32 %result
}

define i32 @mulhhurn_28(i32 %a, i32 %b) {
; CHECK-LABEL: mulhhurn_28:
; CHECK: seal5.cv.mulhhurn {{.*}}, 28{{$}}
; CHECK: ret
  %ahalf = lshr i32 %a, 16
  %bhalf = lshr i32 %b, 16
  %product = mul i32 %ahalf, %bhalf
  %rounded = add i32 %product, 134217728
  %result = lshr i32 %rounded, 28
  ret i32 %result
}

define i32 @mulhhurn_29(i32 %a, i32 %b) {
; CHECK-LABEL: mulhhurn_29:
; CHECK: seal5.cv.mulhhurn {{.*}}, 29{{$}}
; CHECK: ret
  %ahalf = lshr i32 %a, 16
  %bhalf = lshr i32 %b, 16
  %product = mul i32 %ahalf, %bhalf
  %rounded = add i32 %product, 268435456
  %result = lshr i32 %rounded, 29
  ret i32 %result
}

define i32 @mulhhurn_30(i32 %a, i32 %b) {
; CHECK-LABEL: mulhhurn_30:
; CHECK: seal5.cv.mulhhurn {{.*}}, 30{{$}}
; CHECK: ret
  %ahalf = lshr i32 %a, 16
  %bhalf = lshr i32 %b, 16
  %product = mul i32 %ahalf, %bhalf
  %rounded = add i32 %product, 536870912
  %result = lshr i32 %rounded, 30
  ret i32 %result
}

define i32 @mulhhurn_31(i32 %a, i32 %b) {
; CHECK-LABEL: mulhhurn_31:
; CHECK: seal5.cv.mulhhurn {{.*}}, 31{{$}}
; CHECK: ret
  %ahalf = lshr i32 %a, 16
  %bhalf = lshr i32 %b, 16
  %product = mul i32 %ahalf, %bhalf
  %rounded = add i32 %product, 1073741824
  %result = lshr i32 %rounded, 31
  ret i32 %result
}

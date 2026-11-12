; RUN: llc -O0 -mtriple=riscv32 -mattr=+m,+xcorevmac -verify-machineinstrs -global-isel=0 -global-isel-abort=1 < %s | FileCheck %s
; RUN: llc -O3 -mtriple=riscv32 -mattr=+m,+xcorevmac -verify-machineinstrs -global-isel=0 -global-isel-abort=1 < %s | FileCheck %s
; RUN: llc -O0 -mtriple=riscv32 -mattr=+m,+xcorevmac -verify-machineinstrs -global-isel=1 -global-isel-abort=1 < %s | FileCheck %s
; RUN: llc -O3 -mtriple=riscv32 -mattr=+m,+xcorevmac -verify-machineinstrs -global-isel=1 -global-isel-abort=1 < %s | FileCheck %s

define i32 @mulhhsrn_0(i32 %a, i32 %b) {
; CHECK-LABEL: mulhhsrn_0:
; CHECK: seal5.cv.mulhhs{{r?}}n {{.*}}, 0{{$}}
; CHECK: ret
  %ahalf = ashr i32 %a, 16
  %bhalf = ashr i32 %b, 16
  %product = mul i32 %ahalf, %bhalf
  ret i32 %product
}

define i32 @mulhhsrn_1(i32 %a, i32 %b) {
; CHECK-LABEL: mulhhsrn_1:
; CHECK: seal5.cv.mulhhsrn {{.*}}, 1{{$}}
; CHECK: ret
  %ahalf = ashr i32 %a, 16
  %bhalf = ashr i32 %b, 16
  %product = mul i32 %ahalf, %bhalf
  %rounded = add i32 %product, 1
  %result = ashr i32 %rounded, 1
  ret i32 %result
}

define i32 @mulhhsrn_2(i32 %a, i32 %b) {
; CHECK-LABEL: mulhhsrn_2:
; CHECK: seal5.cv.mulhhsrn {{.*}}, 2{{$}}
; CHECK: ret
  %ahalf = ashr i32 %a, 16
  %bhalf = ashr i32 %b, 16
  %product = mul i32 %ahalf, %bhalf
  %rounded = add i32 %product, 2
  %result = ashr i32 %rounded, 2
  ret i32 %result
}

define i32 @mulhhsrn_3(i32 %a, i32 %b) {
; CHECK-LABEL: mulhhsrn_3:
; CHECK: seal5.cv.mulhhsrn {{.*}}, 3{{$}}
; CHECK: ret
  %ahalf = ashr i32 %a, 16
  %bhalf = ashr i32 %b, 16
  %product = mul i32 %ahalf, %bhalf
  %rounded = add i32 %product, 4
  %result = ashr i32 %rounded, 3
  ret i32 %result
}

define i32 @mulhhsrn_4(i32 %a, i32 %b) {
; CHECK-LABEL: mulhhsrn_4:
; CHECK: seal5.cv.mulhhsrn {{.*}}, 4{{$}}
; CHECK: ret
  %ahalf = ashr i32 %a, 16
  %bhalf = ashr i32 %b, 16
  %product = mul i32 %ahalf, %bhalf
  %rounded = add i32 %product, 8
  %result = ashr i32 %rounded, 4
  ret i32 %result
}

define i32 @mulhhsrn_5(i32 %a, i32 %b) {
; CHECK-LABEL: mulhhsrn_5:
; CHECK: seal5.cv.mulhhsrn {{.*}}, 5{{$}}
; CHECK: ret
  %ahalf = ashr i32 %a, 16
  %bhalf = ashr i32 %b, 16
  %product = mul i32 %ahalf, %bhalf
  %rounded = add i32 %product, 16
  %result = ashr i32 %rounded, 5
  ret i32 %result
}

define i32 @mulhhsrn_6(i32 %a, i32 %b) {
; CHECK-LABEL: mulhhsrn_6:
; CHECK: seal5.cv.mulhhsrn {{.*}}, 6{{$}}
; CHECK: ret
  %ahalf = ashr i32 %a, 16
  %bhalf = ashr i32 %b, 16
  %product = mul i32 %ahalf, %bhalf
  %rounded = add i32 %product, 32
  %result = ashr i32 %rounded, 6
  ret i32 %result
}

define i32 @mulhhsrn_7(i32 %a, i32 %b) {
; CHECK-LABEL: mulhhsrn_7:
; CHECK: seal5.cv.mulhhsrn {{.*}}, 7{{$}}
; CHECK: ret
  %ahalf = ashr i32 %a, 16
  %bhalf = ashr i32 %b, 16
  %product = mul i32 %ahalf, %bhalf
  %rounded = add i32 %product, 64
  %result = ashr i32 %rounded, 7
  ret i32 %result
}

define i32 @mulhhsrn_8(i32 %a, i32 %b) {
; CHECK-LABEL: mulhhsrn_8:
; CHECK: seal5.cv.mulhhsrn {{.*}}, 8{{$}}
; CHECK: ret
  %ahalf = ashr i32 %a, 16
  %bhalf = ashr i32 %b, 16
  %product = mul i32 %ahalf, %bhalf
  %rounded = add i32 %product, 128
  %result = ashr i32 %rounded, 8
  ret i32 %result
}

define i32 @mulhhsrn_9(i32 %a, i32 %b) {
; CHECK-LABEL: mulhhsrn_9:
; CHECK: seal5.cv.mulhhsrn {{.*}}, 9{{$}}
; CHECK: ret
  %ahalf = ashr i32 %a, 16
  %bhalf = ashr i32 %b, 16
  %product = mul i32 %ahalf, %bhalf
  %rounded = add i32 %product, 256
  %result = ashr i32 %rounded, 9
  ret i32 %result
}

define i32 @mulhhsrn_10(i32 %a, i32 %b) {
; CHECK-LABEL: mulhhsrn_10:
; CHECK: seal5.cv.mulhhsrn {{.*}}, 10{{$}}
; CHECK: ret
  %ahalf = ashr i32 %a, 16
  %bhalf = ashr i32 %b, 16
  %product = mul i32 %ahalf, %bhalf
  %rounded = add i32 %product, 512
  %result = ashr i32 %rounded, 10
  ret i32 %result
}

define i32 @mulhhsrn_11(i32 %a, i32 %b) {
; CHECK-LABEL: mulhhsrn_11:
; CHECK: seal5.cv.mulhhsrn {{.*}}, 11{{$}}
; CHECK: ret
  %ahalf = ashr i32 %a, 16
  %bhalf = ashr i32 %b, 16
  %product = mul i32 %ahalf, %bhalf
  %rounded = add i32 %product, 1024
  %result = ashr i32 %rounded, 11
  ret i32 %result
}

define i32 @mulhhsrn_12(i32 %a, i32 %b) {
; CHECK-LABEL: mulhhsrn_12:
; CHECK: seal5.cv.mulhhsrn {{.*}}, 12{{$}}
; CHECK: ret
  %ahalf = ashr i32 %a, 16
  %bhalf = ashr i32 %b, 16
  %product = mul i32 %ahalf, %bhalf
  %rounded = add i32 %product, 2048
  %result = ashr i32 %rounded, 12
  ret i32 %result
}

define i32 @mulhhsrn_13(i32 %a, i32 %b) {
; CHECK-LABEL: mulhhsrn_13:
; CHECK: seal5.cv.mulhhsrn {{.*}}, 13{{$}}
; CHECK: ret
  %ahalf = ashr i32 %a, 16
  %bhalf = ashr i32 %b, 16
  %product = mul i32 %ahalf, %bhalf
  %rounded = add i32 %product, 4096
  %result = ashr i32 %rounded, 13
  ret i32 %result
}

define i32 @mulhhsrn_14(i32 %a, i32 %b) {
; CHECK-LABEL: mulhhsrn_14:
; CHECK: seal5.cv.mulhhsrn {{.*}}, 14{{$}}
; CHECK: ret
  %ahalf = ashr i32 %a, 16
  %bhalf = ashr i32 %b, 16
  %product = mul i32 %ahalf, %bhalf
  %rounded = add i32 %product, 8192
  %result = ashr i32 %rounded, 14
  ret i32 %result
}

define i32 @mulhhsrn_15(i32 %a, i32 %b) {
; CHECK-LABEL: mulhhsrn_15:
; CHECK: seal5.cv.mulhhsrn {{.*}}, 15{{$}}
; CHECK: ret
  %ahalf = ashr i32 %a, 16
  %bhalf = ashr i32 %b, 16
  %product = mul i32 %ahalf, %bhalf
  %rounded = add i32 %product, 16384
  %result = ashr i32 %rounded, 15
  ret i32 %result
}

define i32 @mulhhsrn_16(i32 %a, i32 %b) {
; CHECK-LABEL: mulhhsrn_16:
; CHECK: seal5.cv.mulhhsrn {{.*}}, 16{{$}}
; CHECK: ret
  %ahalf = ashr i32 %a, 16
  %bhalf = ashr i32 %b, 16
  %product = mul i32 %ahalf, %bhalf
  %rounded = add i32 %product, 32768
  %result = ashr i32 %rounded, 16
  ret i32 %result
}

define i32 @mulhhsrn_17(i32 %a, i32 %b) {
; CHECK-LABEL: mulhhsrn_17:
; CHECK: seal5.cv.mulhhsrn {{.*}}, 17{{$}}
; CHECK: ret
  %ahalf = ashr i32 %a, 16
  %bhalf = ashr i32 %b, 16
  %product = mul i32 %ahalf, %bhalf
  %rounded = add i32 %product, 65536
  %result = ashr i32 %rounded, 17
  ret i32 %result
}

define i32 @mulhhsrn_18(i32 %a, i32 %b) {
; CHECK-LABEL: mulhhsrn_18:
; CHECK: seal5.cv.mulhhsrn {{.*}}, 18{{$}}
; CHECK: ret
  %ahalf = ashr i32 %a, 16
  %bhalf = ashr i32 %b, 16
  %product = mul i32 %ahalf, %bhalf
  %rounded = add i32 %product, 131072
  %result = ashr i32 %rounded, 18
  ret i32 %result
}

define i32 @mulhhsrn_19(i32 %a, i32 %b) {
; CHECK-LABEL: mulhhsrn_19:
; CHECK: seal5.cv.mulhhsrn {{.*}}, 19{{$}}
; CHECK: ret
  %ahalf = ashr i32 %a, 16
  %bhalf = ashr i32 %b, 16
  %product = mul i32 %ahalf, %bhalf
  %rounded = add i32 %product, 262144
  %result = ashr i32 %rounded, 19
  ret i32 %result
}

define i32 @mulhhsrn_20(i32 %a, i32 %b) {
; CHECK-LABEL: mulhhsrn_20:
; CHECK: seal5.cv.mulhhsrn {{.*}}, 20{{$}}
; CHECK: ret
  %ahalf = ashr i32 %a, 16
  %bhalf = ashr i32 %b, 16
  %product = mul i32 %ahalf, %bhalf
  %rounded = add i32 %product, 524288
  %result = ashr i32 %rounded, 20
  ret i32 %result
}

define i32 @mulhhsrn_21(i32 %a, i32 %b) {
; CHECK-LABEL: mulhhsrn_21:
; CHECK: seal5.cv.mulhhsrn {{.*}}, 21{{$}}
; CHECK: ret
  %ahalf = ashr i32 %a, 16
  %bhalf = ashr i32 %b, 16
  %product = mul i32 %ahalf, %bhalf
  %rounded = add i32 %product, 1048576
  %result = ashr i32 %rounded, 21
  ret i32 %result
}

define i32 @mulhhsrn_22(i32 %a, i32 %b) {
; CHECK-LABEL: mulhhsrn_22:
; CHECK: seal5.cv.mulhhsrn {{.*}}, 22{{$}}
; CHECK: ret
  %ahalf = ashr i32 %a, 16
  %bhalf = ashr i32 %b, 16
  %product = mul i32 %ahalf, %bhalf
  %rounded = add i32 %product, 2097152
  %result = ashr i32 %rounded, 22
  ret i32 %result
}

define i32 @mulhhsrn_23(i32 %a, i32 %b) {
; CHECK-LABEL: mulhhsrn_23:
; CHECK: seal5.cv.mulhhsrn {{.*}}, 23{{$}}
; CHECK: ret
  %ahalf = ashr i32 %a, 16
  %bhalf = ashr i32 %b, 16
  %product = mul i32 %ahalf, %bhalf
  %rounded = add i32 %product, 4194304
  %result = ashr i32 %rounded, 23
  ret i32 %result
}

define i32 @mulhhsrn_24(i32 %a, i32 %b) {
; CHECK-LABEL: mulhhsrn_24:
; CHECK: seal5.cv.mulhhsrn {{.*}}, 24{{$}}
; CHECK: ret
  %ahalf = ashr i32 %a, 16
  %bhalf = ashr i32 %b, 16
  %product = mul i32 %ahalf, %bhalf
  %rounded = add i32 %product, 8388608
  %result = ashr i32 %rounded, 24
  ret i32 %result
}

define i32 @mulhhsrn_25(i32 %a, i32 %b) {
; CHECK-LABEL: mulhhsrn_25:
; CHECK: seal5.cv.mulhhsrn {{.*}}, 25{{$}}
; CHECK: ret
  %ahalf = ashr i32 %a, 16
  %bhalf = ashr i32 %b, 16
  %product = mul i32 %ahalf, %bhalf
  %rounded = add i32 %product, 16777216
  %result = ashr i32 %rounded, 25
  ret i32 %result
}

define i32 @mulhhsrn_26(i32 %a, i32 %b) {
; CHECK-LABEL: mulhhsrn_26:
; CHECK: seal5.cv.mulhhsrn {{.*}}, 26{{$}}
; CHECK: ret
  %ahalf = ashr i32 %a, 16
  %bhalf = ashr i32 %b, 16
  %product = mul i32 %ahalf, %bhalf
  %rounded = add i32 %product, 33554432
  %result = ashr i32 %rounded, 26
  ret i32 %result
}

define i32 @mulhhsrn_27(i32 %a, i32 %b) {
; CHECK-LABEL: mulhhsrn_27:
; CHECK: seal5.cv.mulhhsrn {{.*}}, 27{{$}}
; CHECK: ret
  %ahalf = ashr i32 %a, 16
  %bhalf = ashr i32 %b, 16
  %product = mul i32 %ahalf, %bhalf
  %rounded = add i32 %product, 67108864
  %result = ashr i32 %rounded, 27
  ret i32 %result
}

define i32 @mulhhsrn_28(i32 %a, i32 %b) {
; CHECK-LABEL: mulhhsrn_28:
; CHECK: seal5.cv.mulhhsrn {{.*}}, 28{{$}}
; CHECK: ret
  %ahalf = ashr i32 %a, 16
  %bhalf = ashr i32 %b, 16
  %product = mul i32 %ahalf, %bhalf
  %rounded = add i32 %product, 134217728
  %result = ashr i32 %rounded, 28
  ret i32 %result
}

define i32 @mulhhsrn_29(i32 %a, i32 %b) {
; CHECK-LABEL: mulhhsrn_29:
; CHECK: seal5.cv.mulhhsrn {{.*}}, 29{{$}}
; CHECK: ret
  %ahalf = ashr i32 %a, 16
  %bhalf = ashr i32 %b, 16
  %product = mul i32 %ahalf, %bhalf
  %rounded = add i32 %product, 268435456
  %result = ashr i32 %rounded, 29
  ret i32 %result
}

define i32 @mulhhsrn_30(i32 %a, i32 %b) {
; CHECK-LABEL: mulhhsrn_30:
; CHECK: seal5.cv.mulhhsrn {{.*}}, 30{{$}}
; CHECK: ret
  %ahalf = ashr i32 %a, 16
  %bhalf = ashr i32 %b, 16
  %product = mul i32 %ahalf, %bhalf
  %rounded = add i32 %product, 536870912
  %result = ashr i32 %rounded, 30
  ret i32 %result
}

define i32 @mulhhsrn_31(i32 %a, i32 %b) {
; CHECK-LABEL: mulhhsrn_31:
; CHECK: seal5.cv.mulhhsrn {{.*}}, 31{{$}}
; CHECK: ret
  %ahalf = ashr i32 %a, 16
  %bhalf = ashr i32 %b, 16
  %product = mul i32 %ahalf, %bhalf
  %rounded = add i32 %product, 1073741824
  %result = ashr i32 %rounded, 31
  ret i32 %result
}

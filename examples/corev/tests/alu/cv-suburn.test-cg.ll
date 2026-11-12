; RUN: llc -O0 -mtriple=riscv32 -mattr=+m,+xcorevalu -verify-machineinstrs -global-isel=0 -global-isel-abort=1 < %s | FileCheck %s
; RUN: llc -O3 -mtriple=riscv32 -mattr=+m,+xcorevalu -verify-machineinstrs -global-isel=0 -global-isel-abort=1 < %s | FileCheck %s
; RUN: llc -O0 -mtriple=riscv32 -mattr=+m,+xcorevalu -verify-machineinstrs -global-isel=1 -global-isel-abort=1 < %s | FileCheck %s
; RUN: llc -O3 -mtriple=riscv32 -mattr=+m,+xcorevalu -verify-machineinstrs -global-isel=1 -global-isel-abort=1 < %s | FileCheck %s

define i32 @suburn_0(i32 %a, i32 %b) {
; CHECK-LABEL: suburn_0:
; CHECK: seal5.cv.sub{{u?}}RN {{.*}}, 0{{$}}
; CHECK: ret
  %base = sub i32 %a, %b
  ret i32 %base
}

define i32 @suburn_1(i32 %a, i32 %b) {
; CHECK-LABEL: suburn_1:
; CHECK: seal5.cv.subuRN {{.*}}, 1{{$}}
; CHECK: ret
  %base = sub i32 %a, %b
  %rounded = add i32 %base, 1
  %result = lshr i32 %rounded, 1
  ret i32 %result
}

define i32 @suburn_2(i32 %a, i32 %b) {
; CHECK-LABEL: suburn_2:
; CHECK: seal5.cv.subuRN {{.*}}, 2{{$}}
; CHECK: ret
  %base = sub i32 %a, %b
  %rounded = add i32 %base, 2
  %result = lshr i32 %rounded, 2
  ret i32 %result
}

define i32 @suburn_3(i32 %a, i32 %b) {
; CHECK-LABEL: suburn_3:
; CHECK: seal5.cv.subuRN {{.*}}, 3{{$}}
; CHECK: ret
  %base = sub i32 %a, %b
  %rounded = add i32 %base, 4
  %result = lshr i32 %rounded, 3
  ret i32 %result
}

define i32 @suburn_4(i32 %a, i32 %b) {
; CHECK-LABEL: suburn_4:
; CHECK: seal5.cv.subuRN {{.*}}, 4{{$}}
; CHECK: ret
  %base = sub i32 %a, %b
  %rounded = add i32 %base, 8
  %result = lshr i32 %rounded, 4
  ret i32 %result
}

define i32 @suburn_5(i32 %a, i32 %b) {
; CHECK-LABEL: suburn_5:
; CHECK: seal5.cv.subuRN {{.*}}, 5{{$}}
; CHECK: ret
  %base = sub i32 %a, %b
  %rounded = add i32 %base, 16
  %result = lshr i32 %rounded, 5
  ret i32 %result
}

define i32 @suburn_6(i32 %a, i32 %b) {
; CHECK-LABEL: suburn_6:
; CHECK: seal5.cv.subuRN {{.*}}, 6{{$}}
; CHECK: ret
  %base = sub i32 %a, %b
  %rounded = add i32 %base, 32
  %result = lshr i32 %rounded, 6
  ret i32 %result
}

define i32 @suburn_7(i32 %a, i32 %b) {
; CHECK-LABEL: suburn_7:
; CHECK: seal5.cv.subuRN {{.*}}, 7{{$}}
; CHECK: ret
  %base = sub i32 %a, %b
  %rounded = add i32 %base, 64
  %result = lshr i32 %rounded, 7
  ret i32 %result
}

define i32 @suburn_8(i32 %a, i32 %b) {
; CHECK-LABEL: suburn_8:
; CHECK: seal5.cv.subuRN {{.*}}, 8{{$}}
; CHECK: ret
  %base = sub i32 %a, %b
  %rounded = add i32 %base, 128
  %result = lshr i32 %rounded, 8
  ret i32 %result
}

define i32 @suburn_9(i32 %a, i32 %b) {
; CHECK-LABEL: suburn_9:
; CHECK: seal5.cv.subuRN {{.*}}, 9{{$}}
; CHECK: ret
  %base = sub i32 %a, %b
  %rounded = add i32 %base, 256
  %result = lshr i32 %rounded, 9
  ret i32 %result
}

define i32 @suburn_10(i32 %a, i32 %b) {
; CHECK-LABEL: suburn_10:
; CHECK: seal5.cv.subuRN {{.*}}, 10{{$}}
; CHECK: ret
  %base = sub i32 %a, %b
  %rounded = add i32 %base, 512
  %result = lshr i32 %rounded, 10
  ret i32 %result
}

define i32 @suburn_11(i32 %a, i32 %b) {
; CHECK-LABEL: suburn_11:
; CHECK: seal5.cv.subuRN {{.*}}, 11{{$}}
; CHECK: ret
  %base = sub i32 %a, %b
  %rounded = add i32 %base, 1024
  %result = lshr i32 %rounded, 11
  ret i32 %result
}

define i32 @suburn_12(i32 %a, i32 %b) {
; CHECK-LABEL: suburn_12:
; CHECK: seal5.cv.subuRN {{.*}}, 12{{$}}
; CHECK: ret
  %base = sub i32 %a, %b
  %rounded = add i32 %base, 2048
  %result = lshr i32 %rounded, 12
  ret i32 %result
}

define i32 @suburn_13(i32 %a, i32 %b) {
; CHECK-LABEL: suburn_13:
; CHECK: seal5.cv.subuRN {{.*}}, 13{{$}}
; CHECK: ret
  %base = sub i32 %a, %b
  %rounded = add i32 %base, 4096
  %result = lshr i32 %rounded, 13
  ret i32 %result
}

define i32 @suburn_14(i32 %a, i32 %b) {
; CHECK-LABEL: suburn_14:
; CHECK: seal5.cv.subuRN {{.*}}, 14{{$}}
; CHECK: ret
  %base = sub i32 %a, %b
  %rounded = add i32 %base, 8192
  %result = lshr i32 %rounded, 14
  ret i32 %result
}

define i32 @suburn_15(i32 %a, i32 %b) {
; CHECK-LABEL: suburn_15:
; CHECK: seal5.cv.subuRN {{.*}}, 15{{$}}
; CHECK: ret
  %base = sub i32 %a, %b
  %rounded = add i32 %base, 16384
  %result = lshr i32 %rounded, 15
  ret i32 %result
}

define i32 @suburn_16(i32 %a, i32 %b) {
; CHECK-LABEL: suburn_16:
; CHECK: seal5.cv.subuRN {{.*}}, 16{{$}}
; CHECK: ret
  %base = sub i32 %a, %b
  %rounded = add i32 %base, 32768
  %result = lshr i32 %rounded, 16
  ret i32 %result
}

define i32 @suburn_17(i32 %a, i32 %b) {
; CHECK-LABEL: suburn_17:
; CHECK: seal5.cv.subuRN {{.*}}, 17{{$}}
; CHECK: ret
  %base = sub i32 %a, %b
  %rounded = add i32 %base, 65536
  %result = lshr i32 %rounded, 17
  ret i32 %result
}

define i32 @suburn_18(i32 %a, i32 %b) {
; CHECK-LABEL: suburn_18:
; CHECK: seal5.cv.subuRN {{.*}}, 18{{$}}
; CHECK: ret
  %base = sub i32 %a, %b
  %rounded = add i32 %base, 131072
  %result = lshr i32 %rounded, 18
  ret i32 %result
}

define i32 @suburn_19(i32 %a, i32 %b) {
; CHECK-LABEL: suburn_19:
; CHECK: seal5.cv.subuRN {{.*}}, 19{{$}}
; CHECK: ret
  %base = sub i32 %a, %b
  %rounded = add i32 %base, 262144
  %result = lshr i32 %rounded, 19
  ret i32 %result
}

define i32 @suburn_20(i32 %a, i32 %b) {
; CHECK-LABEL: suburn_20:
; CHECK: seal5.cv.subuRN {{.*}}, 20{{$}}
; CHECK: ret
  %base = sub i32 %a, %b
  %rounded = add i32 %base, 524288
  %result = lshr i32 %rounded, 20
  ret i32 %result
}

define i32 @suburn_21(i32 %a, i32 %b) {
; CHECK-LABEL: suburn_21:
; CHECK: seal5.cv.subuRN {{.*}}, 21{{$}}
; CHECK: ret
  %base = sub i32 %a, %b
  %rounded = add i32 %base, 1048576
  %result = lshr i32 %rounded, 21
  ret i32 %result
}

define i32 @suburn_22(i32 %a, i32 %b) {
; CHECK-LABEL: suburn_22:
; CHECK: seal5.cv.subuRN {{.*}}, 22{{$}}
; CHECK: ret
  %base = sub i32 %a, %b
  %rounded = add i32 %base, 2097152
  %result = lshr i32 %rounded, 22
  ret i32 %result
}

define i32 @suburn_23(i32 %a, i32 %b) {
; CHECK-LABEL: suburn_23:
; CHECK: seal5.cv.subuRN {{.*}}, 23{{$}}
; CHECK: ret
  %base = sub i32 %a, %b
  %rounded = add i32 %base, 4194304
  %result = lshr i32 %rounded, 23
  ret i32 %result
}

define i32 @suburn_24(i32 %a, i32 %b) {
; CHECK-LABEL: suburn_24:
; CHECK: seal5.cv.subuRN {{.*}}, 24{{$}}
; CHECK: ret
  %base = sub i32 %a, %b
  %rounded = add i32 %base, 8388608
  %result = lshr i32 %rounded, 24
  ret i32 %result
}

define i32 @suburn_25(i32 %a, i32 %b) {
; CHECK-LABEL: suburn_25:
; CHECK: seal5.cv.subuRN {{.*}}, 25{{$}}
; CHECK: ret
  %base = sub i32 %a, %b
  %rounded = add i32 %base, 16777216
  %result = lshr i32 %rounded, 25
  ret i32 %result
}

define i32 @suburn_26(i32 %a, i32 %b) {
; CHECK-LABEL: suburn_26:
; CHECK: seal5.cv.subuRN {{.*}}, 26{{$}}
; CHECK: ret
  %base = sub i32 %a, %b
  %rounded = add i32 %base, 33554432
  %result = lshr i32 %rounded, 26
  ret i32 %result
}

define i32 @suburn_27(i32 %a, i32 %b) {
; CHECK-LABEL: suburn_27:
; CHECK: seal5.cv.subuRN {{.*}}, 27{{$}}
; CHECK: ret
  %base = sub i32 %a, %b
  %rounded = add i32 %base, 67108864
  %result = lshr i32 %rounded, 27
  ret i32 %result
}

define i32 @suburn_28(i32 %a, i32 %b) {
; CHECK-LABEL: suburn_28:
; CHECK: seal5.cv.subuRN {{.*}}, 28{{$}}
; CHECK: ret
  %base = sub i32 %a, %b
  %rounded = add i32 %base, 134217728
  %result = lshr i32 %rounded, 28
  ret i32 %result
}

define i32 @suburn_29(i32 %a, i32 %b) {
; CHECK-LABEL: suburn_29:
; CHECK: seal5.cv.subuRN {{.*}}, 29{{$}}
; CHECK: ret
  %base = sub i32 %a, %b
  %rounded = add i32 %base, 268435456
  %result = lshr i32 %rounded, 29
  ret i32 %result
}

define i32 @suburn_30(i32 %a, i32 %b) {
; CHECK-LABEL: suburn_30:
; CHECK: seal5.cv.subuRN {{.*}}, 30{{$}}
; CHECK: ret
  %base = sub i32 %a, %b
  %rounded = add i32 %base, 536870912
  %result = lshr i32 %rounded, 30
  ret i32 %result
}

define i32 @suburn_31(i32 %a, i32 %b) {
; CHECK-LABEL: suburn_31:
; CHECK: seal5.cv.subuRN {{.*}}, 31{{$}}
; CHECK: ret
  %base = sub i32 %a, %b
  %rounded = add i32 %base, 1073741824
  %result = lshr i32 %rounded, 31
  ret i32 %result
}

; Optimized IR can move the rounding constant before the subtraction.

define i32 @suburn_1_reassociated(i32 %a, i32 %b) {
; CHECK-LABEL: suburn_1_reassociated:
; CHECK: seal5.cv.subuRN {{.*}}, 1{{$}}
; CHECK: ret
  %rounded_a = add i32 %a, 1
  %difference = sub i32 %rounded_a, %b
  %result = lshr i32 %difference, 1
  ret i32 %result
}

define i32 @suburn_2_reassociated(i32 %a, i32 %b) {
; CHECK-LABEL: suburn_2_reassociated:
; CHECK: seal5.cv.subuRN {{.*}}, 2{{$}}
; CHECK: ret
  %rounded_a = add i32 %a, 2
  %difference = sub i32 %rounded_a, %b
  %result = lshr i32 %difference, 2
  ret i32 %result
}

define i32 @suburn_3_reassociated(i32 %a, i32 %b) {
; CHECK-LABEL: suburn_3_reassociated:
; CHECK: seal5.cv.subuRN {{.*}}, 3{{$}}
; CHECK: ret
  %rounded_a = add i32 %a, 4
  %difference = sub i32 %rounded_a, %b
  %result = lshr i32 %difference, 3
  ret i32 %result
}

define i32 @suburn_4_reassociated(i32 %a, i32 %b) {
; CHECK-LABEL: suburn_4_reassociated:
; CHECK: seal5.cv.subuRN {{.*}}, 4{{$}}
; CHECK: ret
  %rounded_a = add i32 %a, 8
  %difference = sub i32 %rounded_a, %b
  %result = lshr i32 %difference, 4
  ret i32 %result
}

define i32 @suburn_5_reassociated(i32 %a, i32 %b) {
; CHECK-LABEL: suburn_5_reassociated:
; CHECK: seal5.cv.subuRN {{.*}}, 5{{$}}
; CHECK: ret
  %rounded_a = add i32 %a, 16
  %difference = sub i32 %rounded_a, %b
  %result = lshr i32 %difference, 5
  ret i32 %result
}

define i32 @suburn_6_reassociated(i32 %a, i32 %b) {
; CHECK-LABEL: suburn_6_reassociated:
; CHECK: seal5.cv.subuRN {{.*}}, 6{{$}}
; CHECK: ret
  %rounded_a = add i32 %a, 32
  %difference = sub i32 %rounded_a, %b
  %result = lshr i32 %difference, 6
  ret i32 %result
}

define i32 @suburn_7_reassociated(i32 %a, i32 %b) {
; CHECK-LABEL: suburn_7_reassociated:
; CHECK: seal5.cv.subuRN {{.*}}, 7{{$}}
; CHECK: ret
  %rounded_a = add i32 %a, 64
  %difference = sub i32 %rounded_a, %b
  %result = lshr i32 %difference, 7
  ret i32 %result
}

define i32 @suburn_8_reassociated(i32 %a, i32 %b) {
; CHECK-LABEL: suburn_8_reassociated:
; CHECK: seal5.cv.subuRN {{.*}}, 8{{$}}
; CHECK: ret
  %rounded_a = add i32 %a, 128
  %difference = sub i32 %rounded_a, %b
  %result = lshr i32 %difference, 8
  ret i32 %result
}

define i32 @suburn_9_reassociated(i32 %a, i32 %b) {
; CHECK-LABEL: suburn_9_reassociated:
; CHECK: seal5.cv.subuRN {{.*}}, 9{{$}}
; CHECK: ret
  %rounded_a = add i32 %a, 256
  %difference = sub i32 %rounded_a, %b
  %result = lshr i32 %difference, 9
  ret i32 %result
}

define i32 @suburn_10_reassociated(i32 %a, i32 %b) {
; CHECK-LABEL: suburn_10_reassociated:
; CHECK: seal5.cv.subuRN {{.*}}, 10{{$}}
; CHECK: ret
  %rounded_a = add i32 %a, 512
  %difference = sub i32 %rounded_a, %b
  %result = lshr i32 %difference, 10
  ret i32 %result
}

define i32 @suburn_11_reassociated(i32 %a, i32 %b) {
; CHECK-LABEL: suburn_11_reassociated:
; CHECK: seal5.cv.subuRN {{.*}}, 11{{$}}
; CHECK: ret
  %rounded_a = add i32 %a, 1024
  %difference = sub i32 %rounded_a, %b
  %result = lshr i32 %difference, 11
  ret i32 %result
}

define i32 @suburn_12_reassociated(i32 %a, i32 %b) {
; CHECK-LABEL: suburn_12_reassociated:
; CHECK: seal5.cv.subuRN {{.*}}, 12{{$}}
; CHECK: ret
  %rounded_a = add i32 %a, 2048
  %difference = sub i32 %rounded_a, %b
  %result = lshr i32 %difference, 12
  ret i32 %result
}

define i32 @suburn_13_reassociated(i32 %a, i32 %b) {
; CHECK-LABEL: suburn_13_reassociated:
; CHECK: seal5.cv.subuRN {{.*}}, 13{{$}}
; CHECK: ret
  %rounded_a = add i32 %a, 4096
  %difference = sub i32 %rounded_a, %b
  %result = lshr i32 %difference, 13
  ret i32 %result
}

define i32 @suburn_14_reassociated(i32 %a, i32 %b) {
; CHECK-LABEL: suburn_14_reassociated:
; CHECK: seal5.cv.subuRN {{.*}}, 14{{$}}
; CHECK: ret
  %rounded_a = add i32 %a, 8192
  %difference = sub i32 %rounded_a, %b
  %result = lshr i32 %difference, 14
  ret i32 %result
}

define i32 @suburn_15_reassociated(i32 %a, i32 %b) {
; CHECK-LABEL: suburn_15_reassociated:
; CHECK: seal5.cv.subuRN {{.*}}, 15{{$}}
; CHECK: ret
  %rounded_a = add i32 %a, 16384
  %difference = sub i32 %rounded_a, %b
  %result = lshr i32 %difference, 15
  ret i32 %result
}

define i32 @suburn_16_reassociated(i32 %a, i32 %b) {
; CHECK-LABEL: suburn_16_reassociated:
; CHECK: seal5.cv.subuRN {{.*}}, 16{{$}}
; CHECK: ret
  %rounded_a = add i32 %a, 32768
  %difference = sub i32 %rounded_a, %b
  %result = lshr i32 %difference, 16
  ret i32 %result
}

define i32 @suburn_17_reassociated(i32 %a, i32 %b) {
; CHECK-LABEL: suburn_17_reassociated:
; CHECK: seal5.cv.subuRN {{.*}}, 17{{$}}
; CHECK: ret
  %rounded_a = add i32 %a, 65536
  %difference = sub i32 %rounded_a, %b
  %result = lshr i32 %difference, 17
  ret i32 %result
}

define i32 @suburn_18_reassociated(i32 %a, i32 %b) {
; CHECK-LABEL: suburn_18_reassociated:
; CHECK: seal5.cv.subuRN {{.*}}, 18{{$}}
; CHECK: ret
  %rounded_a = add i32 %a, 131072
  %difference = sub i32 %rounded_a, %b
  %result = lshr i32 %difference, 18
  ret i32 %result
}

define i32 @suburn_19_reassociated(i32 %a, i32 %b) {
; CHECK-LABEL: suburn_19_reassociated:
; CHECK: seal5.cv.subuRN {{.*}}, 19{{$}}
; CHECK: ret
  %rounded_a = add i32 %a, 262144
  %difference = sub i32 %rounded_a, %b
  %result = lshr i32 %difference, 19
  ret i32 %result
}

define i32 @suburn_20_reassociated(i32 %a, i32 %b) {
; CHECK-LABEL: suburn_20_reassociated:
; CHECK: seal5.cv.subuRN {{.*}}, 20{{$}}
; CHECK: ret
  %rounded_a = add i32 %a, 524288
  %difference = sub i32 %rounded_a, %b
  %result = lshr i32 %difference, 20
  ret i32 %result
}

define i32 @suburn_21_reassociated(i32 %a, i32 %b) {
; CHECK-LABEL: suburn_21_reassociated:
; CHECK: seal5.cv.subuRN {{.*}}, 21{{$}}
; CHECK: ret
  %rounded_a = add i32 %a, 1048576
  %difference = sub i32 %rounded_a, %b
  %result = lshr i32 %difference, 21
  ret i32 %result
}

define i32 @suburn_22_reassociated(i32 %a, i32 %b) {
; CHECK-LABEL: suburn_22_reassociated:
; CHECK: seal5.cv.subuRN {{.*}}, 22{{$}}
; CHECK: ret
  %rounded_a = add i32 %a, 2097152
  %difference = sub i32 %rounded_a, %b
  %result = lshr i32 %difference, 22
  ret i32 %result
}

define i32 @suburn_23_reassociated(i32 %a, i32 %b) {
; CHECK-LABEL: suburn_23_reassociated:
; CHECK: seal5.cv.subuRN {{.*}}, 23{{$}}
; CHECK: ret
  %rounded_a = add i32 %a, 4194304
  %difference = sub i32 %rounded_a, %b
  %result = lshr i32 %difference, 23
  ret i32 %result
}

define i32 @suburn_24_reassociated(i32 %a, i32 %b) {
; CHECK-LABEL: suburn_24_reassociated:
; CHECK: seal5.cv.subuRN {{.*}}, 24{{$}}
; CHECK: ret
  %rounded_a = add i32 %a, 8388608
  %difference = sub i32 %rounded_a, %b
  %result = lshr i32 %difference, 24
  ret i32 %result
}

define i32 @suburn_25_reassociated(i32 %a, i32 %b) {
; CHECK-LABEL: suburn_25_reassociated:
; CHECK: seal5.cv.subuRN {{.*}}, 25{{$}}
; CHECK: ret
  %rounded_a = add i32 %a, 16777216
  %difference = sub i32 %rounded_a, %b
  %result = lshr i32 %difference, 25
  ret i32 %result
}

define i32 @suburn_26_reassociated(i32 %a, i32 %b) {
; CHECK-LABEL: suburn_26_reassociated:
; CHECK: seal5.cv.subuRN {{.*}}, 26{{$}}
; CHECK: ret
  %rounded_a = add i32 %a, 33554432
  %difference = sub i32 %rounded_a, %b
  %result = lshr i32 %difference, 26
  ret i32 %result
}

define i32 @suburn_27_reassociated(i32 %a, i32 %b) {
; CHECK-LABEL: suburn_27_reassociated:
; CHECK: seal5.cv.subuRN {{.*}}, 27{{$}}
; CHECK: ret
  %rounded_a = add i32 %a, 67108864
  %difference = sub i32 %rounded_a, %b
  %result = lshr i32 %difference, 27
  ret i32 %result
}

define i32 @suburn_28_reassociated(i32 %a, i32 %b) {
; CHECK-LABEL: suburn_28_reassociated:
; CHECK: seal5.cv.subuRN {{.*}}, 28{{$}}
; CHECK: ret
  %rounded_a = add i32 %a, 134217728
  %difference = sub i32 %rounded_a, %b
  %result = lshr i32 %difference, 28
  ret i32 %result
}

define i32 @suburn_29_reassociated(i32 %a, i32 %b) {
; CHECK-LABEL: suburn_29_reassociated:
; CHECK: seal5.cv.subuRN {{.*}}, 29{{$}}
; CHECK: ret
  %rounded_a = add i32 %a, 268435456
  %difference = sub i32 %rounded_a, %b
  %result = lshr i32 %difference, 29
  ret i32 %result
}

define i32 @suburn_30_reassociated(i32 %a, i32 %b) {
; CHECK-LABEL: suburn_30_reassociated:
; CHECK: seal5.cv.subuRN {{.*}}, 30{{$}}
; CHECK: ret
  %rounded_a = add i32 %a, 536870912
  %difference = sub i32 %rounded_a, %b
  %result = lshr i32 %difference, 30
  ret i32 %result
}

define i32 @suburn_31_reassociated(i32 %a, i32 %b) {
; CHECK-LABEL: suburn_31_reassociated:
; CHECK: seal5.cv.subuRN {{.*}}, 31{{$}}
; CHECK: ret
  %rounded_a = add i32 %a, 1073741824
  %difference = sub i32 %rounded_a, %b
  %result = lshr i32 %difference, 31
  ret i32 %result
}

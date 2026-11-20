; RUN: llc -O0 -mtriple=riscv32 -mattr=+m,+xcorevalu -verify-machineinstrs -global-isel=0 -global-isel-abort=1 < %s | FileCheck %s
; RUN: llc -O3 -mtriple=riscv32 -mattr=+m,+xcorevalu -verify-machineinstrs -global-isel=0 -global-isel-abort=1 < %s | FileCheck %s
; RUN: llc -O0 -mtriple=riscv32 -mattr=+m,+xcorevalu -verify-machineinstrs -global-isel=1 -global-isel-abort=1 < %s | FileCheck %s
; RUN: llc -O3 -mtriple=riscv32 -mattr=+m,+xcorevalu -verify-machineinstrs -global-isel=1 -global-isel-abort=1 < %s | FileCheck %s

declare i32 @llvm.smin.i32(i32, i32)
declare i32 @llvm.smax.i32(i32, i32)

define i32 @clip_0(i32 %a) {
; CHECK-LABEL: clip_0:
; CHECK: seal5.cv.clip a0, a0, {{[01]}}{{$}}
; CHECK: ret
  %lo = call i32 @llvm.smax.i32(i32 %a, i32 -1)
  %hi = call i32 @llvm.smin.i32(i32 %lo, i32 0)
  ret i32 %hi
}

define i32 @clip_1(i32 %a) {
; CHECK-LABEL: clip_1:
; CHECK: seal5.cv.clip a0, a0, {{[01]}}{{$}}
; CHECK: ret
  %lo = call i32 @llvm.smax.i32(i32 %a, i32 -1)
  %hi = call i32 @llvm.smin.i32(i32 %lo, i32 0)
  ret i32 %hi
}

define i32 @clip_2(i32 %a) {
; CHECK-LABEL: clip_2:
; CHECK: seal5.cv.clip a0, a0, 2{{$}}
; CHECK: ret
  %lo = call i32 @llvm.smax.i32(i32 %a, i32 -2)
  %hi = call i32 @llvm.smin.i32(i32 %lo, i32 1)
  ret i32 %hi
}

define i32 @clip_3(i32 %a) {
; CHECK-LABEL: clip_3:
; CHECK: seal5.cv.clip a0, a0, 3{{$}}
; CHECK: ret
  %lo = call i32 @llvm.smax.i32(i32 %a, i32 -4)
  %hi = call i32 @llvm.smin.i32(i32 %lo, i32 3)
  ret i32 %hi
}

define i32 @clip_4(i32 %a) {
; CHECK-LABEL: clip_4:
; CHECK: seal5.cv.clip a0, a0, 4{{$}}
; CHECK: ret
  %lo = call i32 @llvm.smax.i32(i32 %a, i32 -8)
  %hi = call i32 @llvm.smin.i32(i32 %lo, i32 7)
  ret i32 %hi
}

define i32 @clip_5(i32 %a) {
; CHECK-LABEL: clip_5:
; CHECK: seal5.cv.clip a0, a0, 5{{$}}
; CHECK: ret
  %lo = call i32 @llvm.smax.i32(i32 %a, i32 -16)
  %hi = call i32 @llvm.smin.i32(i32 %lo, i32 15)
  ret i32 %hi
}

define i32 @clip_6(i32 %a) {
; CHECK-LABEL: clip_6:
; CHECK: seal5.cv.clip a0, a0, 6{{$}}
; CHECK: ret
  %lo = call i32 @llvm.smax.i32(i32 %a, i32 -32)
  %hi = call i32 @llvm.smin.i32(i32 %lo, i32 31)
  ret i32 %hi
}

define i32 @clip_7(i32 %a) {
; CHECK-LABEL: clip_7:
; CHECK: seal5.cv.clip a0, a0, 7{{$}}
; CHECK: ret
  %lo = call i32 @llvm.smax.i32(i32 %a, i32 -64)
  %hi = call i32 @llvm.smin.i32(i32 %lo, i32 63)
  ret i32 %hi
}

define i32 @clip_8(i32 %a) {
; CHECK-LABEL: clip_8:
; CHECK: seal5.cv.clip a0, a0, 8{{$}}
; CHECK: ret
  %lo = call i32 @llvm.smax.i32(i32 %a, i32 -128)
  %hi = call i32 @llvm.smin.i32(i32 %lo, i32 127)
  ret i32 %hi
}

define i32 @clip_9(i32 %a) {
; CHECK-LABEL: clip_9:
; CHECK: seal5.cv.clip a0, a0, 9{{$}}
; CHECK: ret
  %lo = call i32 @llvm.smax.i32(i32 %a, i32 -256)
  %hi = call i32 @llvm.smin.i32(i32 %lo, i32 255)
  ret i32 %hi
}

define i32 @clip_10(i32 %a) {
; CHECK-LABEL: clip_10:
; CHECK: seal5.cv.clip a0, a0, 10{{$}}
; CHECK: ret
  %lo = call i32 @llvm.smax.i32(i32 %a, i32 -512)
  %hi = call i32 @llvm.smin.i32(i32 %lo, i32 511)
  ret i32 %hi
}

define i32 @clip_11(i32 %a) {
; CHECK-LABEL: clip_11:
; CHECK: seal5.cv.clip a0, a0, 11{{$}}
; CHECK: ret
  %lo = call i32 @llvm.smax.i32(i32 %a, i32 -1024)
  %hi = call i32 @llvm.smin.i32(i32 %lo, i32 1023)
  ret i32 %hi
}

define i32 @clip_12(i32 %a) {
; CHECK-LABEL: clip_12:
; CHECK: seal5.cv.clip a0, a0, 12{{$}}
; CHECK: ret
  %lo = call i32 @llvm.smax.i32(i32 %a, i32 -2048)
  %hi = call i32 @llvm.smin.i32(i32 %lo, i32 2047)
  ret i32 %hi
}

define i32 @clip_13(i32 %a) {
; CHECK-LABEL: clip_13:
; CHECK: seal5.cv.clip a0, a0, 13{{$}}
; CHECK: ret
  %lo = call i32 @llvm.smax.i32(i32 %a, i32 -4096)
  %hi = call i32 @llvm.smin.i32(i32 %lo, i32 4095)
  ret i32 %hi
}

define i32 @clip_14(i32 %a) {
; CHECK-LABEL: clip_14:
; CHECK: seal5.cv.clip a0, a0, 14{{$}}
; CHECK: ret
  %lo = call i32 @llvm.smax.i32(i32 %a, i32 -8192)
  %hi = call i32 @llvm.smin.i32(i32 %lo, i32 8191)
  ret i32 %hi
}

define i32 @clip_15(i32 %a) {
; CHECK-LABEL: clip_15:
; CHECK: seal5.cv.clip a0, a0, 15{{$}}
; CHECK: ret
  %lo = call i32 @llvm.smax.i32(i32 %a, i32 -16384)
  %hi = call i32 @llvm.smin.i32(i32 %lo, i32 16383)
  ret i32 %hi
}

define i32 @clip_16(i32 %a) {
; CHECK-LABEL: clip_16:
; CHECK: seal5.cv.clip a0, a0, 16{{$}}
; CHECK: ret
  %lo = call i32 @llvm.smax.i32(i32 %a, i32 -32768)
  %hi = call i32 @llvm.smin.i32(i32 %lo, i32 32767)
  ret i32 %hi
}

define i32 @clip_17(i32 %a) {
; CHECK-LABEL: clip_17:
; CHECK: seal5.cv.clip a0, a0, 17{{$}}
; CHECK: ret
  %lo = call i32 @llvm.smax.i32(i32 %a, i32 -65536)
  %hi = call i32 @llvm.smin.i32(i32 %lo, i32 65535)
  ret i32 %hi
}

define i32 @clip_18(i32 %a) {
; CHECK-LABEL: clip_18:
; CHECK: seal5.cv.clip a0, a0, 18{{$}}
; CHECK: ret
  %lo = call i32 @llvm.smax.i32(i32 %a, i32 -131072)
  %hi = call i32 @llvm.smin.i32(i32 %lo, i32 131071)
  ret i32 %hi
}

define i32 @clip_19(i32 %a) {
; CHECK-LABEL: clip_19:
; CHECK: seal5.cv.clip a0, a0, 19{{$}}
; CHECK: ret
  %lo = call i32 @llvm.smax.i32(i32 %a, i32 -262144)
  %hi = call i32 @llvm.smin.i32(i32 %lo, i32 262143)
  ret i32 %hi
}

define i32 @clip_20(i32 %a) {
; CHECK-LABEL: clip_20:
; CHECK: seal5.cv.clip a0, a0, 20{{$}}
; CHECK: ret
  %lo = call i32 @llvm.smax.i32(i32 %a, i32 -524288)
  %hi = call i32 @llvm.smin.i32(i32 %lo, i32 524287)
  ret i32 %hi
}

define i32 @clip_21(i32 %a) {
; CHECK-LABEL: clip_21:
; CHECK: seal5.cv.clip a0, a0, 21{{$}}
; CHECK: ret
  %lo = call i32 @llvm.smax.i32(i32 %a, i32 -1048576)
  %hi = call i32 @llvm.smin.i32(i32 %lo, i32 1048575)
  ret i32 %hi
}

define i32 @clip_22(i32 %a) {
; CHECK-LABEL: clip_22:
; CHECK: seal5.cv.clip a0, a0, 22{{$}}
; CHECK: ret
  %lo = call i32 @llvm.smax.i32(i32 %a, i32 -2097152)
  %hi = call i32 @llvm.smin.i32(i32 %lo, i32 2097151)
  ret i32 %hi
}

define i32 @clip_23(i32 %a) {
; CHECK-LABEL: clip_23:
; CHECK: seal5.cv.clip a0, a0, 23{{$}}
; CHECK: ret
  %lo = call i32 @llvm.smax.i32(i32 %a, i32 -4194304)
  %hi = call i32 @llvm.smin.i32(i32 %lo, i32 4194303)
  ret i32 %hi
}

define i32 @clip_24(i32 %a) {
; CHECK-LABEL: clip_24:
; CHECK: seal5.cv.clip a0, a0, 24{{$}}
; CHECK: ret
  %lo = call i32 @llvm.smax.i32(i32 %a, i32 -8388608)
  %hi = call i32 @llvm.smin.i32(i32 %lo, i32 8388607)
  ret i32 %hi
}

define i32 @clip_25(i32 %a) {
; CHECK-LABEL: clip_25:
; CHECK: seal5.cv.clip a0, a0, 25{{$}}
; CHECK: ret
  %lo = call i32 @llvm.smax.i32(i32 %a, i32 -16777216)
  %hi = call i32 @llvm.smin.i32(i32 %lo, i32 16777215)
  ret i32 %hi
}

define i32 @clip_26(i32 %a) {
; CHECK-LABEL: clip_26:
; CHECK: seal5.cv.clip a0, a0, 26{{$}}
; CHECK: ret
  %lo = call i32 @llvm.smax.i32(i32 %a, i32 -33554432)
  %hi = call i32 @llvm.smin.i32(i32 %lo, i32 33554431)
  ret i32 %hi
}

define i32 @clip_27(i32 %a) {
; CHECK-LABEL: clip_27:
; CHECK: seal5.cv.clip a0, a0, 27{{$}}
; CHECK: ret
  %lo = call i32 @llvm.smax.i32(i32 %a, i32 -67108864)
  %hi = call i32 @llvm.smin.i32(i32 %lo, i32 67108863)
  ret i32 %hi
}

define i32 @clip_28(i32 %a) {
; CHECK-LABEL: clip_28:
; CHECK: seal5.cv.clip a0, a0, 28{{$}}
; CHECK: ret
  %lo = call i32 @llvm.smax.i32(i32 %a, i32 -134217728)
  %hi = call i32 @llvm.smin.i32(i32 %lo, i32 134217727)
  ret i32 %hi
}

define i32 @clip_29(i32 %a) {
; CHECK-LABEL: clip_29:
; CHECK: seal5.cv.clip a0, a0, 29{{$}}
; CHECK: ret
  %lo = call i32 @llvm.smax.i32(i32 %a, i32 -268435456)
  %hi = call i32 @llvm.smin.i32(i32 %lo, i32 268435455)
  ret i32 %hi
}

define i32 @clip_30(i32 %a) {
; CHECK-LABEL: clip_30:
; CHECK: seal5.cv.clip a0, a0, 30{{$}}
; CHECK: ret
  %lo = call i32 @llvm.smax.i32(i32 %a, i32 -536870912)
  %hi = call i32 @llvm.smin.i32(i32 %lo, i32 536870911)
  ret i32 %hi
}

define i32 @clip_31(i32 %a) {
; CHECK-LABEL: clip_31:
; CHECK: seal5.cv.clip a0, a0, 31{{$}}
; CHECK: ret
  %lo = call i32 @llvm.smax.i32(i32 %a, i32 -1073741824)
  %hi = call i32 @llvm.smin.i32(i32 %lo, i32 1073741823)
  ret i32 %hi
}

define i32 @clip_0_upper_first(i32 %a) {
; CHECK-LABEL: clip_0_upper_first:
; CHECK: seal5.cv.clip a0, a0, {{[01]}}{{$}}
; CHECK: ret
  %hi = call i32 @llvm.smin.i32(i32 %a, i32 0)
  %lo = call i32 @llvm.smax.i32(i32 %hi, i32 -1)
  ret i32 %lo
}


define i32 @clip_1_upper_first(i32 %a) {
; CHECK-LABEL: clip_1_upper_first:
; CHECK: seal5.cv.clip a0, a0, {{[01]}}{{$}}
; CHECK: ret
  %hi = call i32 @llvm.smin.i32(i32 %a, i32 0)
  %lo = call i32 @llvm.smax.i32(i32 %hi, i32 -1)
  ret i32 %lo
}


define i32 @clip_2_upper_first(i32 %a) {
; CHECK-LABEL: clip_2_upper_first:
; CHECK: seal5.cv.clip a0, a0, 2{{$}}
; CHECK: ret
  %hi = call i32 @llvm.smin.i32(i32 %a, i32 1)
  %lo = call i32 @llvm.smax.i32(i32 %hi, i32 -2)
  ret i32 %lo
}


define i32 @clip_3_upper_first(i32 %a) {
; CHECK-LABEL: clip_3_upper_first:
; CHECK: seal5.cv.clip a0, a0, 3{{$}}
; CHECK: ret
  %hi = call i32 @llvm.smin.i32(i32 %a, i32 3)
  %lo = call i32 @llvm.smax.i32(i32 %hi, i32 -4)
  ret i32 %lo
}


define i32 @clip_4_upper_first(i32 %a) {
; CHECK-LABEL: clip_4_upper_first:
; CHECK: seal5.cv.clip a0, a0, 4{{$}}
; CHECK: ret
  %hi = call i32 @llvm.smin.i32(i32 %a, i32 7)
  %lo = call i32 @llvm.smax.i32(i32 %hi, i32 -8)
  ret i32 %lo
}


define i32 @clip_5_upper_first(i32 %a) {
; CHECK-LABEL: clip_5_upper_first:
; CHECK: seal5.cv.clip a0, a0, 5{{$}}
; CHECK: ret
  %hi = call i32 @llvm.smin.i32(i32 %a, i32 15)
  %lo = call i32 @llvm.smax.i32(i32 %hi, i32 -16)
  ret i32 %lo
}


define i32 @clip_6_upper_first(i32 %a) {
; CHECK-LABEL: clip_6_upper_first:
; CHECK: seal5.cv.clip a0, a0, 6{{$}}
; CHECK: ret
  %hi = call i32 @llvm.smin.i32(i32 %a, i32 31)
  %lo = call i32 @llvm.smax.i32(i32 %hi, i32 -32)
  ret i32 %lo
}


define i32 @clip_7_upper_first(i32 %a) {
; CHECK-LABEL: clip_7_upper_first:
; CHECK: seal5.cv.clip a0, a0, 7{{$}}
; CHECK: ret
  %hi = call i32 @llvm.smin.i32(i32 %a, i32 63)
  %lo = call i32 @llvm.smax.i32(i32 %hi, i32 -64)
  ret i32 %lo
}


define i32 @clip_8_upper_first(i32 %a) {
; CHECK-LABEL: clip_8_upper_first:
; CHECK: seal5.cv.clip a0, a0, 8{{$}}
; CHECK: ret
  %hi = call i32 @llvm.smin.i32(i32 %a, i32 127)
  %lo = call i32 @llvm.smax.i32(i32 %hi, i32 -128)
  ret i32 %lo
}


define i32 @clip_9_upper_first(i32 %a) {
; CHECK-LABEL: clip_9_upper_first:
; CHECK: seal5.cv.clip a0, a0, 9{{$}}
; CHECK: ret
  %hi = call i32 @llvm.smin.i32(i32 %a, i32 255)
  %lo = call i32 @llvm.smax.i32(i32 %hi, i32 -256)
  ret i32 %lo
}


define i32 @clip_10_upper_first(i32 %a) {
; CHECK-LABEL: clip_10_upper_first:
; CHECK: seal5.cv.clip a0, a0, 10{{$}}
; CHECK: ret
  %hi = call i32 @llvm.smin.i32(i32 %a, i32 511)
  %lo = call i32 @llvm.smax.i32(i32 %hi, i32 -512)
  ret i32 %lo
}


define i32 @clip_11_upper_first(i32 %a) {
; CHECK-LABEL: clip_11_upper_first:
; CHECK: seal5.cv.clip a0, a0, 11{{$}}
; CHECK: ret
  %hi = call i32 @llvm.smin.i32(i32 %a, i32 1023)
  %lo = call i32 @llvm.smax.i32(i32 %hi, i32 -1024)
  ret i32 %lo
}


define i32 @clip_12_upper_first(i32 %a) {
; CHECK-LABEL: clip_12_upper_first:
; CHECK: seal5.cv.clip a0, a0, 12{{$}}
; CHECK: ret
  %hi = call i32 @llvm.smin.i32(i32 %a, i32 2047)
  %lo = call i32 @llvm.smax.i32(i32 %hi, i32 -2048)
  ret i32 %lo
}


define i32 @clip_13_upper_first(i32 %a) {
; CHECK-LABEL: clip_13_upper_first:
; CHECK: seal5.cv.clip a0, a0, 13{{$}}
; CHECK: ret
  %hi = call i32 @llvm.smin.i32(i32 %a, i32 4095)
  %lo = call i32 @llvm.smax.i32(i32 %hi, i32 -4096)
  ret i32 %lo
}


define i32 @clip_14_upper_first(i32 %a) {
; CHECK-LABEL: clip_14_upper_first:
; CHECK: seal5.cv.clip a0, a0, 14{{$}}
; CHECK: ret
  %hi = call i32 @llvm.smin.i32(i32 %a, i32 8191)
  %lo = call i32 @llvm.smax.i32(i32 %hi, i32 -8192)
  ret i32 %lo
}


define i32 @clip_15_upper_first(i32 %a) {
; CHECK-LABEL: clip_15_upper_first:
; CHECK: seal5.cv.clip a0, a0, 15{{$}}
; CHECK: ret
  %hi = call i32 @llvm.smin.i32(i32 %a, i32 16383)
  %lo = call i32 @llvm.smax.i32(i32 %hi, i32 -16384)
  ret i32 %lo
}


define i32 @clip_16_upper_first(i32 %a) {
; CHECK-LABEL: clip_16_upper_first:
; CHECK: seal5.cv.clip a0, a0, 16{{$}}
; CHECK: ret
  %hi = call i32 @llvm.smin.i32(i32 %a, i32 32767)
  %lo = call i32 @llvm.smax.i32(i32 %hi, i32 -32768)
  ret i32 %lo
}


define i32 @clip_17_upper_first(i32 %a) {
; CHECK-LABEL: clip_17_upper_first:
; CHECK: seal5.cv.clip a0, a0, 17{{$}}
; CHECK: ret
  %hi = call i32 @llvm.smin.i32(i32 %a, i32 65535)
  %lo = call i32 @llvm.smax.i32(i32 %hi, i32 -65536)
  ret i32 %lo
}


define i32 @clip_18_upper_first(i32 %a) {
; CHECK-LABEL: clip_18_upper_first:
; CHECK: seal5.cv.clip a0, a0, 18{{$}}
; CHECK: ret
  %hi = call i32 @llvm.smin.i32(i32 %a, i32 131071)
  %lo = call i32 @llvm.smax.i32(i32 %hi, i32 -131072)
  ret i32 %lo
}


define i32 @clip_19_upper_first(i32 %a) {
; CHECK-LABEL: clip_19_upper_first:
; CHECK: seal5.cv.clip a0, a0, 19{{$}}
; CHECK: ret
  %hi = call i32 @llvm.smin.i32(i32 %a, i32 262143)
  %lo = call i32 @llvm.smax.i32(i32 %hi, i32 -262144)
  ret i32 %lo
}


define i32 @clip_20_upper_first(i32 %a) {
; CHECK-LABEL: clip_20_upper_first:
; CHECK: seal5.cv.clip a0, a0, 20{{$}}
; CHECK: ret
  %hi = call i32 @llvm.smin.i32(i32 %a, i32 524287)
  %lo = call i32 @llvm.smax.i32(i32 %hi, i32 -524288)
  ret i32 %lo
}


define i32 @clip_21_upper_first(i32 %a) {
; CHECK-LABEL: clip_21_upper_first:
; CHECK: seal5.cv.clip a0, a0, 21{{$}}
; CHECK: ret
  %hi = call i32 @llvm.smin.i32(i32 %a, i32 1048575)
  %lo = call i32 @llvm.smax.i32(i32 %hi, i32 -1048576)
  ret i32 %lo
}


define i32 @clip_22_upper_first(i32 %a) {
; CHECK-LABEL: clip_22_upper_first:
; CHECK: seal5.cv.clip a0, a0, 22{{$}}
; CHECK: ret
  %hi = call i32 @llvm.smin.i32(i32 %a, i32 2097151)
  %lo = call i32 @llvm.smax.i32(i32 %hi, i32 -2097152)
  ret i32 %lo
}


define i32 @clip_23_upper_first(i32 %a) {
; CHECK-LABEL: clip_23_upper_first:
; CHECK: seal5.cv.clip a0, a0, 23{{$}}
; CHECK: ret
  %hi = call i32 @llvm.smin.i32(i32 %a, i32 4194303)
  %lo = call i32 @llvm.smax.i32(i32 %hi, i32 -4194304)
  ret i32 %lo
}


define i32 @clip_24_upper_first(i32 %a) {
; CHECK-LABEL: clip_24_upper_first:
; CHECK: seal5.cv.clip a0, a0, 24{{$}}
; CHECK: ret
  %hi = call i32 @llvm.smin.i32(i32 %a, i32 8388607)
  %lo = call i32 @llvm.smax.i32(i32 %hi, i32 -8388608)
  ret i32 %lo
}


define i32 @clip_25_upper_first(i32 %a) {
; CHECK-LABEL: clip_25_upper_first:
; CHECK: seal5.cv.clip a0, a0, 25{{$}}
; CHECK: ret
  %hi = call i32 @llvm.smin.i32(i32 %a, i32 16777215)
  %lo = call i32 @llvm.smax.i32(i32 %hi, i32 -16777216)
  ret i32 %lo
}


define i32 @clip_26_upper_first(i32 %a) {
; CHECK-LABEL: clip_26_upper_first:
; CHECK: seal5.cv.clip a0, a0, 26{{$}}
; CHECK: ret
  %hi = call i32 @llvm.smin.i32(i32 %a, i32 33554431)
  %lo = call i32 @llvm.smax.i32(i32 %hi, i32 -33554432)
  ret i32 %lo
}


define i32 @clip_27_upper_first(i32 %a) {
; CHECK-LABEL: clip_27_upper_first:
; CHECK: seal5.cv.clip a0, a0, 27{{$}}
; CHECK: ret
  %hi = call i32 @llvm.smin.i32(i32 %a, i32 67108863)
  %lo = call i32 @llvm.smax.i32(i32 %hi, i32 -67108864)
  ret i32 %lo
}


define i32 @clip_28_upper_first(i32 %a) {
; CHECK-LABEL: clip_28_upper_first:
; CHECK: seal5.cv.clip a0, a0, 28{{$}}
; CHECK: ret
  %hi = call i32 @llvm.smin.i32(i32 %a, i32 134217727)
  %lo = call i32 @llvm.smax.i32(i32 %hi, i32 -134217728)
  ret i32 %lo
}


define i32 @clip_29_upper_first(i32 %a) {
; CHECK-LABEL: clip_29_upper_first:
; CHECK: seal5.cv.clip a0, a0, 29{{$}}
; CHECK: ret
  %hi = call i32 @llvm.smin.i32(i32 %a, i32 268435455)
  %lo = call i32 @llvm.smax.i32(i32 %hi, i32 -268435456)
  ret i32 %lo
}


define i32 @clip_30_upper_first(i32 %a) {
; CHECK-LABEL: clip_30_upper_first:
; CHECK: seal5.cv.clip a0, a0, 30{{$}}
; CHECK: ret
  %hi = call i32 @llvm.smin.i32(i32 %a, i32 536870911)
  %lo = call i32 @llvm.smax.i32(i32 %hi, i32 -536870912)
  ret i32 %lo
}


define i32 @clip_31_upper_first(i32 %a) {
; CHECK-LABEL: clip_31_upper_first:
; CHECK: seal5.cv.clip a0, a0, 31{{$}}
; CHECK: ret
  %hi = call i32 @llvm.smin.i32(i32 %a, i32 1073741823)
  %lo = call i32 @llvm.smax.i32(i32 %hi, i32 -1073741824)
  ret i32 %lo
}

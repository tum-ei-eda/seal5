; RUN: llc -O0 -mtriple=riscv32 -mattr=+m,+xcorevalu -verify-machineinstrs -global-isel=0 -global-isel-abort=1 < %s | FileCheck %s
; RUN: llc -O3 -mtriple=riscv32 -mattr=+m,+xcorevalu -verify-machineinstrs -global-isel=0 -global-isel-abort=1 < %s | FileCheck %s
; RUN: llc -O0 -mtriple=riscv32 -mattr=+m,+xcorevalu -verify-machineinstrs -global-isel=1 -global-isel-abort=1 < %s | FileCheck %s
; RUN: llc -O3 -mtriple=riscv32 -mattr=+m,+xcorevalu -verify-machineinstrs -global-isel=1 -global-isel-abort=1 < %s | FileCheck %s

declare i32 @llvm.smin.i32(i32, i32)
declare i32 @llvm.smax.i32(i32, i32)

define i32 @clipu_0(i32 %a) {
; CHECK-LABEL: clipu_0:
; CHECK: li a0, 0
; CHECK-NOT: seal5.cv.clip
; CHECK: ret
  ret i32 0
}

define i32 @clipu_1(i32 %a) {
; CHECK-LABEL: clipu_1:
; CHECK: li a0, 0
; CHECK-NOT: seal5.cv.clip
; CHECK: ret
  ret i32 0
}

define i32 @clipu_2(i32 %a) {
; CHECK-LABEL: clipu_2:
; CHECK: seal5.cv.clipu a0, a0, 2{{$}}
; CHECK: ret
  %lo = call i32 @llvm.smax.i32(i32 %a, i32 0)
  %hi = call i32 @llvm.smin.i32(i32 %lo, i32 1)
  ret i32 %hi
}

define i32 @clipu_3(i32 %a) {
; CHECK-LABEL: clipu_3:
; CHECK: seal5.cv.clipu a0, a0, 3{{$}}
; CHECK: ret
  %lo = call i32 @llvm.smax.i32(i32 %a, i32 0)
  %hi = call i32 @llvm.smin.i32(i32 %lo, i32 3)
  ret i32 %hi
}

define i32 @clipu_4(i32 %a) {
; CHECK-LABEL: clipu_4:
; CHECK: seal5.cv.clipu a0, a0, 4{{$}}
; CHECK: ret
  %lo = call i32 @llvm.smax.i32(i32 %a, i32 0)
  %hi = call i32 @llvm.smin.i32(i32 %lo, i32 7)
  ret i32 %hi
}

define i32 @clipu_5(i32 %a) {
; CHECK-LABEL: clipu_5:
; CHECK: seal5.cv.clipu a0, a0, 5{{$}}
; CHECK: ret
  %lo = call i32 @llvm.smax.i32(i32 %a, i32 0)
  %hi = call i32 @llvm.smin.i32(i32 %lo, i32 15)
  ret i32 %hi
}

define i32 @clipu_6(i32 %a) {
; CHECK-LABEL: clipu_6:
; CHECK: seal5.cv.clipu a0, a0, 6{{$}}
; CHECK: ret
  %lo = call i32 @llvm.smax.i32(i32 %a, i32 0)
  %hi = call i32 @llvm.smin.i32(i32 %lo, i32 31)
  ret i32 %hi
}

define i32 @clipu_7(i32 %a) {
; CHECK-LABEL: clipu_7:
; CHECK: seal5.cv.clipu a0, a0, 7{{$}}
; CHECK: ret
  %lo = call i32 @llvm.smax.i32(i32 %a, i32 0)
  %hi = call i32 @llvm.smin.i32(i32 %lo, i32 63)
  ret i32 %hi
}

define i32 @clipu_8(i32 %a) {
; CHECK-LABEL: clipu_8:
; CHECK: seal5.cv.clipu a0, a0, 8{{$}}
; CHECK: ret
  %lo = call i32 @llvm.smax.i32(i32 %a, i32 0)
  %hi = call i32 @llvm.smin.i32(i32 %lo, i32 127)
  ret i32 %hi
}

define i32 @clipu_9(i32 %a) {
; CHECK-LABEL: clipu_9:
; CHECK: seal5.cv.clipu a0, a0, 9{{$}}
; CHECK: ret
  %lo = call i32 @llvm.smax.i32(i32 %a, i32 0)
  %hi = call i32 @llvm.smin.i32(i32 %lo, i32 255)
  ret i32 %hi
}

define i32 @clipu_10(i32 %a) {
; CHECK-LABEL: clipu_10:
; CHECK: seal5.cv.clipu a0, a0, 10{{$}}
; CHECK: ret
  %lo = call i32 @llvm.smax.i32(i32 %a, i32 0)
  %hi = call i32 @llvm.smin.i32(i32 %lo, i32 511)
  ret i32 %hi
}

define i32 @clipu_11(i32 %a) {
; CHECK-LABEL: clipu_11:
; CHECK: seal5.cv.clipu a0, a0, 11{{$}}
; CHECK: ret
  %lo = call i32 @llvm.smax.i32(i32 %a, i32 0)
  %hi = call i32 @llvm.smin.i32(i32 %lo, i32 1023)
  ret i32 %hi
}

define i32 @clipu_12(i32 %a) {
; CHECK-LABEL: clipu_12:
; CHECK: seal5.cv.clipu a0, a0, 12{{$}}
; CHECK: ret
  %lo = call i32 @llvm.smax.i32(i32 %a, i32 0)
  %hi = call i32 @llvm.smin.i32(i32 %lo, i32 2047)
  ret i32 %hi
}

define i32 @clipu_13(i32 %a) {
; CHECK-LABEL: clipu_13:
; CHECK: seal5.cv.clipu a0, a0, 13{{$}}
; CHECK: ret
  %lo = call i32 @llvm.smax.i32(i32 %a, i32 0)
  %hi = call i32 @llvm.smin.i32(i32 %lo, i32 4095)
  ret i32 %hi
}

define i32 @clipu_14(i32 %a) {
; CHECK-LABEL: clipu_14:
; CHECK: seal5.cv.clipu a0, a0, 14{{$}}
; CHECK: ret
  %lo = call i32 @llvm.smax.i32(i32 %a, i32 0)
  %hi = call i32 @llvm.smin.i32(i32 %lo, i32 8191)
  ret i32 %hi
}

define i32 @clipu_15(i32 %a) {
; CHECK-LABEL: clipu_15:
; CHECK: seal5.cv.clipu a0, a0, 15{{$}}
; CHECK: ret
  %lo = call i32 @llvm.smax.i32(i32 %a, i32 0)
  %hi = call i32 @llvm.smin.i32(i32 %lo, i32 16383)
  ret i32 %hi
}

define i32 @clipu_16(i32 %a) {
; CHECK-LABEL: clipu_16:
; CHECK: seal5.cv.clipu a0, a0, 16{{$}}
; CHECK: ret
  %lo = call i32 @llvm.smax.i32(i32 %a, i32 0)
  %hi = call i32 @llvm.smin.i32(i32 %lo, i32 32767)
  ret i32 %hi
}

define i32 @clipu_17(i32 %a) {
; CHECK-LABEL: clipu_17:
; CHECK: seal5.cv.clipu a0, a0, 17{{$}}
; CHECK: ret
  %lo = call i32 @llvm.smax.i32(i32 %a, i32 0)
  %hi = call i32 @llvm.smin.i32(i32 %lo, i32 65535)
  ret i32 %hi
}

define i32 @clipu_18(i32 %a) {
; CHECK-LABEL: clipu_18:
; CHECK: seal5.cv.clipu a0, a0, 18{{$}}
; CHECK: ret
  %lo = call i32 @llvm.smax.i32(i32 %a, i32 0)
  %hi = call i32 @llvm.smin.i32(i32 %lo, i32 131071)
  ret i32 %hi
}

define i32 @clipu_19(i32 %a) {
; CHECK-LABEL: clipu_19:
; CHECK: seal5.cv.clipu a0, a0, 19{{$}}
; CHECK: ret
  %lo = call i32 @llvm.smax.i32(i32 %a, i32 0)
  %hi = call i32 @llvm.smin.i32(i32 %lo, i32 262143)
  ret i32 %hi
}

define i32 @clipu_20(i32 %a) {
; CHECK-LABEL: clipu_20:
; CHECK: seal5.cv.clipu a0, a0, 20{{$}}
; CHECK: ret
  %lo = call i32 @llvm.smax.i32(i32 %a, i32 0)
  %hi = call i32 @llvm.smin.i32(i32 %lo, i32 524287)
  ret i32 %hi
}

define i32 @clipu_21(i32 %a) {
; CHECK-LABEL: clipu_21:
; CHECK: seal5.cv.clipu a0, a0, 21{{$}}
; CHECK: ret
  %lo = call i32 @llvm.smax.i32(i32 %a, i32 0)
  %hi = call i32 @llvm.smin.i32(i32 %lo, i32 1048575)
  ret i32 %hi
}

define i32 @clipu_22(i32 %a) {
; CHECK-LABEL: clipu_22:
; CHECK: seal5.cv.clipu a0, a0, 22{{$}}
; CHECK: ret
  %lo = call i32 @llvm.smax.i32(i32 %a, i32 0)
  %hi = call i32 @llvm.smin.i32(i32 %lo, i32 2097151)
  ret i32 %hi
}

define i32 @clipu_23(i32 %a) {
; CHECK-LABEL: clipu_23:
; CHECK: seal5.cv.clipu a0, a0, 23{{$}}
; CHECK: ret
  %lo = call i32 @llvm.smax.i32(i32 %a, i32 0)
  %hi = call i32 @llvm.smin.i32(i32 %lo, i32 4194303)
  ret i32 %hi
}

define i32 @clipu_24(i32 %a) {
; CHECK-LABEL: clipu_24:
; CHECK: seal5.cv.clipu a0, a0, 24{{$}}
; CHECK: ret
  %lo = call i32 @llvm.smax.i32(i32 %a, i32 0)
  %hi = call i32 @llvm.smin.i32(i32 %lo, i32 8388607)
  ret i32 %hi
}

define i32 @clipu_25(i32 %a) {
; CHECK-LABEL: clipu_25:
; CHECK: seal5.cv.clipu a0, a0, 25{{$}}
; CHECK: ret
  %lo = call i32 @llvm.smax.i32(i32 %a, i32 0)
  %hi = call i32 @llvm.smin.i32(i32 %lo, i32 16777215)
  ret i32 %hi
}

define i32 @clipu_26(i32 %a) {
; CHECK-LABEL: clipu_26:
; CHECK: seal5.cv.clipu a0, a0, 26{{$}}
; CHECK: ret
  %lo = call i32 @llvm.smax.i32(i32 %a, i32 0)
  %hi = call i32 @llvm.smin.i32(i32 %lo, i32 33554431)
  ret i32 %hi
}

define i32 @clipu_27(i32 %a) {
; CHECK-LABEL: clipu_27:
; CHECK: seal5.cv.clipu a0, a0, 27{{$}}
; CHECK: ret
  %lo = call i32 @llvm.smax.i32(i32 %a, i32 0)
  %hi = call i32 @llvm.smin.i32(i32 %lo, i32 67108863)
  ret i32 %hi
}

define i32 @clipu_28(i32 %a) {
; CHECK-LABEL: clipu_28:
; CHECK: seal5.cv.clipu a0, a0, 28{{$}}
; CHECK: ret
  %lo = call i32 @llvm.smax.i32(i32 %a, i32 0)
  %hi = call i32 @llvm.smin.i32(i32 %lo, i32 134217727)
  ret i32 %hi
}

define i32 @clipu_29(i32 %a) {
; CHECK-LABEL: clipu_29:
; CHECK: seal5.cv.clipu a0, a0, 29{{$}}
; CHECK: ret
  %lo = call i32 @llvm.smax.i32(i32 %a, i32 0)
  %hi = call i32 @llvm.smin.i32(i32 %lo, i32 268435455)
  ret i32 %hi
}

define i32 @clipu_30(i32 %a) {
; CHECK-LABEL: clipu_30:
; CHECK: seal5.cv.clipu a0, a0, 30{{$}}
; CHECK: ret
  %lo = call i32 @llvm.smax.i32(i32 %a, i32 0)
  %hi = call i32 @llvm.smin.i32(i32 %lo, i32 536870911)
  ret i32 %hi
}

define i32 @clipu_31(i32 %a) {
; CHECK-LABEL: clipu_31:
; CHECK: seal5.cv.clipu a0, a0, 31{{$}}
; CHECK: ret
  %lo = call i32 @llvm.smax.i32(i32 %a, i32 0)
  %hi = call i32 @llvm.smin.i32(i32 %lo, i32 1073741823)
  ret i32 %hi
}

define i32 @clipu_2_upper_first(i32 %a) {
; CHECK-LABEL: clipu_2_upper_first:
; CHECK: seal5.cv.clipu a0, a0, 2{{$}}
; CHECK: ret
  %hi = call i32 @llvm.smin.i32(i32 %a, i32 1)
  %lo = call i32 @llvm.smax.i32(i32 %hi, i32 0)
  ret i32 %lo
}


define i32 @clipu_3_upper_first(i32 %a) {
; CHECK-LABEL: clipu_3_upper_first:
; CHECK: seal5.cv.clipu a0, a0, 3{{$}}
; CHECK: ret
  %hi = call i32 @llvm.smin.i32(i32 %a, i32 3)
  %lo = call i32 @llvm.smax.i32(i32 %hi, i32 0)
  ret i32 %lo
}


define i32 @clipu_4_upper_first(i32 %a) {
; CHECK-LABEL: clipu_4_upper_first:
; CHECK: seal5.cv.clipu a0, a0, 4{{$}}
; CHECK: ret
  %hi = call i32 @llvm.smin.i32(i32 %a, i32 7)
  %lo = call i32 @llvm.smax.i32(i32 %hi, i32 0)
  ret i32 %lo
}


define i32 @clipu_5_upper_first(i32 %a) {
; CHECK-LABEL: clipu_5_upper_first:
; CHECK: seal5.cv.clipu a0, a0, 5{{$}}
; CHECK: ret
  %hi = call i32 @llvm.smin.i32(i32 %a, i32 15)
  %lo = call i32 @llvm.smax.i32(i32 %hi, i32 0)
  ret i32 %lo
}


define i32 @clipu_6_upper_first(i32 %a) {
; CHECK-LABEL: clipu_6_upper_first:
; CHECK: seal5.cv.clipu a0, a0, 6{{$}}
; CHECK: ret
  %hi = call i32 @llvm.smin.i32(i32 %a, i32 31)
  %lo = call i32 @llvm.smax.i32(i32 %hi, i32 0)
  ret i32 %lo
}


define i32 @clipu_7_upper_first(i32 %a) {
; CHECK-LABEL: clipu_7_upper_first:
; CHECK: seal5.cv.clipu a0, a0, 7{{$}}
; CHECK: ret
  %hi = call i32 @llvm.smin.i32(i32 %a, i32 63)
  %lo = call i32 @llvm.smax.i32(i32 %hi, i32 0)
  ret i32 %lo
}


define i32 @clipu_8_upper_first(i32 %a) {
; CHECK-LABEL: clipu_8_upper_first:
; CHECK: seal5.cv.clipu a0, a0, 8{{$}}
; CHECK: ret
  %hi = call i32 @llvm.smin.i32(i32 %a, i32 127)
  %lo = call i32 @llvm.smax.i32(i32 %hi, i32 0)
  ret i32 %lo
}


define i32 @clipu_9_upper_first(i32 %a) {
; CHECK-LABEL: clipu_9_upper_first:
; CHECK: seal5.cv.clipu a0, a0, 9{{$}}
; CHECK: ret
  %hi = call i32 @llvm.smin.i32(i32 %a, i32 255)
  %lo = call i32 @llvm.smax.i32(i32 %hi, i32 0)
  ret i32 %lo
}


define i32 @clipu_10_upper_first(i32 %a) {
; CHECK-LABEL: clipu_10_upper_first:
; CHECK: seal5.cv.clipu a0, a0, 10{{$}}
; CHECK: ret
  %hi = call i32 @llvm.smin.i32(i32 %a, i32 511)
  %lo = call i32 @llvm.smax.i32(i32 %hi, i32 0)
  ret i32 %lo
}


define i32 @clipu_11_upper_first(i32 %a) {
; CHECK-LABEL: clipu_11_upper_first:
; CHECK: seal5.cv.clipu a0, a0, 11{{$}}
; CHECK: ret
  %hi = call i32 @llvm.smin.i32(i32 %a, i32 1023)
  %lo = call i32 @llvm.smax.i32(i32 %hi, i32 0)
  ret i32 %lo
}


define i32 @clipu_12_upper_first(i32 %a) {
; CHECK-LABEL: clipu_12_upper_first:
; CHECK: seal5.cv.clipu a0, a0, 12{{$}}
; CHECK: ret
  %hi = call i32 @llvm.smin.i32(i32 %a, i32 2047)
  %lo = call i32 @llvm.smax.i32(i32 %hi, i32 0)
  ret i32 %lo
}


define i32 @clipu_13_upper_first(i32 %a) {
; CHECK-LABEL: clipu_13_upper_first:
; CHECK: seal5.cv.clipu a0, a0, 13{{$}}
; CHECK: ret
  %hi = call i32 @llvm.smin.i32(i32 %a, i32 4095)
  %lo = call i32 @llvm.smax.i32(i32 %hi, i32 0)
  ret i32 %lo
}


define i32 @clipu_14_upper_first(i32 %a) {
; CHECK-LABEL: clipu_14_upper_first:
; CHECK: seal5.cv.clipu a0, a0, 14{{$}}
; CHECK: ret
  %hi = call i32 @llvm.smin.i32(i32 %a, i32 8191)
  %lo = call i32 @llvm.smax.i32(i32 %hi, i32 0)
  ret i32 %lo
}


define i32 @clipu_15_upper_first(i32 %a) {
; CHECK-LABEL: clipu_15_upper_first:
; CHECK: seal5.cv.clipu a0, a0, 15{{$}}
; CHECK: ret
  %hi = call i32 @llvm.smin.i32(i32 %a, i32 16383)
  %lo = call i32 @llvm.smax.i32(i32 %hi, i32 0)
  ret i32 %lo
}


define i32 @clipu_16_upper_first(i32 %a) {
; CHECK-LABEL: clipu_16_upper_first:
; CHECK: seal5.cv.clipu a0, a0, 16{{$}}
; CHECK: ret
  %hi = call i32 @llvm.smin.i32(i32 %a, i32 32767)
  %lo = call i32 @llvm.smax.i32(i32 %hi, i32 0)
  ret i32 %lo
}


define i32 @clipu_17_upper_first(i32 %a) {
; CHECK-LABEL: clipu_17_upper_first:
; CHECK: seal5.cv.clipu a0, a0, 17{{$}}
; CHECK: ret
  %hi = call i32 @llvm.smin.i32(i32 %a, i32 65535)
  %lo = call i32 @llvm.smax.i32(i32 %hi, i32 0)
  ret i32 %lo
}


define i32 @clipu_18_upper_first(i32 %a) {
; CHECK-LABEL: clipu_18_upper_first:
; CHECK: seal5.cv.clipu a0, a0, 18{{$}}
; CHECK: ret
  %hi = call i32 @llvm.smin.i32(i32 %a, i32 131071)
  %lo = call i32 @llvm.smax.i32(i32 %hi, i32 0)
  ret i32 %lo
}


define i32 @clipu_19_upper_first(i32 %a) {
; CHECK-LABEL: clipu_19_upper_first:
; CHECK: seal5.cv.clipu a0, a0, 19{{$}}
; CHECK: ret
  %hi = call i32 @llvm.smin.i32(i32 %a, i32 262143)
  %lo = call i32 @llvm.smax.i32(i32 %hi, i32 0)
  ret i32 %lo
}


define i32 @clipu_20_upper_first(i32 %a) {
; CHECK-LABEL: clipu_20_upper_first:
; CHECK: seal5.cv.clipu a0, a0, 20{{$}}
; CHECK: ret
  %hi = call i32 @llvm.smin.i32(i32 %a, i32 524287)
  %lo = call i32 @llvm.smax.i32(i32 %hi, i32 0)
  ret i32 %lo
}


define i32 @clipu_21_upper_first(i32 %a) {
; CHECK-LABEL: clipu_21_upper_first:
; CHECK: seal5.cv.clipu a0, a0, 21{{$}}
; CHECK: ret
  %hi = call i32 @llvm.smin.i32(i32 %a, i32 1048575)
  %lo = call i32 @llvm.smax.i32(i32 %hi, i32 0)
  ret i32 %lo
}


define i32 @clipu_22_upper_first(i32 %a) {
; CHECK-LABEL: clipu_22_upper_first:
; CHECK: seal5.cv.clipu a0, a0, 22{{$}}
; CHECK: ret
  %hi = call i32 @llvm.smin.i32(i32 %a, i32 2097151)
  %lo = call i32 @llvm.smax.i32(i32 %hi, i32 0)
  ret i32 %lo
}


define i32 @clipu_23_upper_first(i32 %a) {
; CHECK-LABEL: clipu_23_upper_first:
; CHECK: seal5.cv.clipu a0, a0, 23{{$}}
; CHECK: ret
  %hi = call i32 @llvm.smin.i32(i32 %a, i32 4194303)
  %lo = call i32 @llvm.smax.i32(i32 %hi, i32 0)
  ret i32 %lo
}


define i32 @clipu_24_upper_first(i32 %a) {
; CHECK-LABEL: clipu_24_upper_first:
; CHECK: seal5.cv.clipu a0, a0, 24{{$}}
; CHECK: ret
  %hi = call i32 @llvm.smin.i32(i32 %a, i32 8388607)
  %lo = call i32 @llvm.smax.i32(i32 %hi, i32 0)
  ret i32 %lo
}


define i32 @clipu_25_upper_first(i32 %a) {
; CHECK-LABEL: clipu_25_upper_first:
; CHECK: seal5.cv.clipu a0, a0, 25{{$}}
; CHECK: ret
  %hi = call i32 @llvm.smin.i32(i32 %a, i32 16777215)
  %lo = call i32 @llvm.smax.i32(i32 %hi, i32 0)
  ret i32 %lo
}


define i32 @clipu_26_upper_first(i32 %a) {
; CHECK-LABEL: clipu_26_upper_first:
; CHECK: seal5.cv.clipu a0, a0, 26{{$}}
; CHECK: ret
  %hi = call i32 @llvm.smin.i32(i32 %a, i32 33554431)
  %lo = call i32 @llvm.smax.i32(i32 %hi, i32 0)
  ret i32 %lo
}


define i32 @clipu_27_upper_first(i32 %a) {
; CHECK-LABEL: clipu_27_upper_first:
; CHECK: seal5.cv.clipu a0, a0, 27{{$}}
; CHECK: ret
  %hi = call i32 @llvm.smin.i32(i32 %a, i32 67108863)
  %lo = call i32 @llvm.smax.i32(i32 %hi, i32 0)
  ret i32 %lo
}


define i32 @clipu_28_upper_first(i32 %a) {
; CHECK-LABEL: clipu_28_upper_first:
; CHECK: seal5.cv.clipu a0, a0, 28{{$}}
; CHECK: ret
  %hi = call i32 @llvm.smin.i32(i32 %a, i32 134217727)
  %lo = call i32 @llvm.smax.i32(i32 %hi, i32 0)
  ret i32 %lo
}


define i32 @clipu_29_upper_first(i32 %a) {
; CHECK-LABEL: clipu_29_upper_first:
; CHECK: seal5.cv.clipu a0, a0, 29{{$}}
; CHECK: ret
  %hi = call i32 @llvm.smin.i32(i32 %a, i32 268435455)
  %lo = call i32 @llvm.smax.i32(i32 %hi, i32 0)
  ret i32 %lo
}


define i32 @clipu_30_upper_first(i32 %a) {
; CHECK-LABEL: clipu_30_upper_first:
; CHECK: seal5.cv.clipu a0, a0, 30{{$}}
; CHECK: ret
  %hi = call i32 @llvm.smin.i32(i32 %a, i32 536870911)
  %lo = call i32 @llvm.smax.i32(i32 %hi, i32 0)
  ret i32 %lo
}


define i32 @clipu_31_upper_first(i32 %a) {
; CHECK-LABEL: clipu_31_upper_first:
; CHECK: seal5.cv.clipu a0, a0, 31{{$}}
; CHECK: ret
  %hi = call i32 @llvm.smin.i32(i32 %a, i32 1073741823)
  %lo = call i32 @llvm.smax.i32(i32 %hi, i32 0)
  ret i32 %lo
}

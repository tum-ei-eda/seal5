; RUN: llc -O0 -mtriple=riscv32 -mattr=+m,+xcorevalu -verify-machineinstrs -global-isel=0 -global-isel-abort=1 < %s | FileCheck %s
; RUN: llc -O3 -mtriple=riscv32 -mattr=+m,+xcorevalu -verify-machineinstrs -global-isel=0 -global-isel-abort=1 < %s | FileCheck %s
; RUN: llc -O0 -mtriple=riscv32 -mattr=+m,+xcorevalu -verify-machineinstrs -global-isel=1 -global-isel-abort=1 < %s | FileCheck %s
; RUN: llc -O3 -mtriple=riscv32 -mattr=+m,+xcorevalu -verify-machineinstrs -global-isel=1 -global-isel-abort=1 < %s | FileCheck %s

define i32 @addurn_0(i32 %a, i32 %b) {
; CHECK-LABEL: addurn_0:
; CHECK: seal5.cv.add{{u?}}RN {{.*}}, 0{{$}}
; CHECK: ret
  %base = add i32 %a, %b
  ret i32 %base
}

define i32 @addurn_1(i32 %a, i32 %b) {
; CHECK-LABEL: addurn_1:
; CHECK: seal5.cv.adduRN {{.*}}, 1{{$}}
; CHECK: ret
  %base = add i32 %a, %b
  %rounded = add i32 %base, 1
  %result = lshr i32 %rounded, 1
  ret i32 %result
}

define i32 @addurn_2(i32 %a, i32 %b) {
; CHECK-LABEL: addurn_2:
; CHECK: seal5.cv.adduRN {{.*}}, 2{{$}}
; CHECK: ret
  %base = add i32 %a, %b
  %rounded = add i32 %base, 2
  %result = lshr i32 %rounded, 2
  ret i32 %result
}

define i32 @addurn_3(i32 %a, i32 %b) {
; CHECK-LABEL: addurn_3:
; CHECK: seal5.cv.adduRN {{.*}}, 3{{$}}
; CHECK: ret
  %base = add i32 %a, %b
  %rounded = add i32 %base, 4
  %result = lshr i32 %rounded, 3
  ret i32 %result
}

define i32 @addurn_4(i32 %a, i32 %b) {
; CHECK-LABEL: addurn_4:
; CHECK: seal5.cv.adduRN {{.*}}, 4{{$}}
; CHECK: ret
  %base = add i32 %a, %b
  %rounded = add i32 %base, 8
  %result = lshr i32 %rounded, 4
  ret i32 %result
}

define i32 @addurn_5(i32 %a, i32 %b) {
; CHECK-LABEL: addurn_5:
; CHECK: seal5.cv.adduRN {{.*}}, 5{{$}}
; CHECK: ret
  %base = add i32 %a, %b
  %rounded = add i32 %base, 16
  %result = lshr i32 %rounded, 5
  ret i32 %result
}

define i32 @addurn_6(i32 %a, i32 %b) {
; CHECK-LABEL: addurn_6:
; CHECK: seal5.cv.adduRN {{.*}}, 6{{$}}
; CHECK: ret
  %base = add i32 %a, %b
  %rounded = add i32 %base, 32
  %result = lshr i32 %rounded, 6
  ret i32 %result
}

define i32 @addurn_7(i32 %a, i32 %b) {
; CHECK-LABEL: addurn_7:
; CHECK: seal5.cv.adduRN {{.*}}, 7{{$}}
; CHECK: ret
  %base = add i32 %a, %b
  %rounded = add i32 %base, 64
  %result = lshr i32 %rounded, 7
  ret i32 %result
}

define i32 @addurn_8(i32 %a, i32 %b) {
; CHECK-LABEL: addurn_8:
; CHECK: seal5.cv.adduRN {{.*}}, 8{{$}}
; CHECK: ret
  %base = add i32 %a, %b
  %rounded = add i32 %base, 128
  %result = lshr i32 %rounded, 8
  ret i32 %result
}

define i32 @addurn_9(i32 %a, i32 %b) {
; CHECK-LABEL: addurn_9:
; CHECK: seal5.cv.adduRN {{.*}}, 9{{$}}
; CHECK: ret
  %base = add i32 %a, %b
  %rounded = add i32 %base, 256
  %result = lshr i32 %rounded, 9
  ret i32 %result
}

define i32 @addurn_10(i32 %a, i32 %b) {
; CHECK-LABEL: addurn_10:
; CHECK: seal5.cv.adduRN {{.*}}, 10{{$}}
; CHECK: ret
  %base = add i32 %a, %b
  %rounded = add i32 %base, 512
  %result = lshr i32 %rounded, 10
  ret i32 %result
}

define i32 @addurn_11(i32 %a, i32 %b) {
; CHECK-LABEL: addurn_11:
; CHECK: seal5.cv.adduRN {{.*}}, 11{{$}}
; CHECK: ret
  %base = add i32 %a, %b
  %rounded = add i32 %base, 1024
  %result = lshr i32 %rounded, 11
  ret i32 %result
}

define i32 @addurn_12(i32 %a, i32 %b) {
; CHECK-LABEL: addurn_12:
; CHECK: seal5.cv.adduRN {{.*}}, 12{{$}}
; CHECK: ret
  %base = add i32 %a, %b
  %rounded = add i32 %base, 2048
  %result = lshr i32 %rounded, 12
  ret i32 %result
}

define i32 @addurn_13(i32 %a, i32 %b) {
; CHECK-LABEL: addurn_13:
; CHECK: seal5.cv.adduRN {{.*}}, 13{{$}}
; CHECK: ret
  %base = add i32 %a, %b
  %rounded = add i32 %base, 4096
  %result = lshr i32 %rounded, 13
  ret i32 %result
}

define i32 @addurn_14(i32 %a, i32 %b) {
; CHECK-LABEL: addurn_14:
; CHECK: seal5.cv.adduRN {{.*}}, 14{{$}}
; CHECK: ret
  %base = add i32 %a, %b
  %rounded = add i32 %base, 8192
  %result = lshr i32 %rounded, 14
  ret i32 %result
}

define i32 @addurn_15(i32 %a, i32 %b) {
; CHECK-LABEL: addurn_15:
; CHECK: seal5.cv.adduRN {{.*}}, 15{{$}}
; CHECK: ret
  %base = add i32 %a, %b
  %rounded = add i32 %base, 16384
  %result = lshr i32 %rounded, 15
  ret i32 %result
}

define i32 @addurn_16(i32 %a, i32 %b) {
; CHECK-LABEL: addurn_16:
; CHECK: seal5.cv.adduRN {{.*}}, 16{{$}}
; CHECK: ret
  %base = add i32 %a, %b
  %rounded = add i32 %base, 32768
  %result = lshr i32 %rounded, 16
  ret i32 %result
}

define i32 @addurn_17(i32 %a, i32 %b) {
; CHECK-LABEL: addurn_17:
; CHECK: seal5.cv.adduRN {{.*}}, 17{{$}}
; CHECK: ret
  %base = add i32 %a, %b
  %rounded = add i32 %base, 65536
  %result = lshr i32 %rounded, 17
  ret i32 %result
}

define i32 @addurn_18(i32 %a, i32 %b) {
; CHECK-LABEL: addurn_18:
; CHECK: seal5.cv.adduRN {{.*}}, 18{{$}}
; CHECK: ret
  %base = add i32 %a, %b
  %rounded = add i32 %base, 131072
  %result = lshr i32 %rounded, 18
  ret i32 %result
}

define i32 @addurn_19(i32 %a, i32 %b) {
; CHECK-LABEL: addurn_19:
; CHECK: seal5.cv.adduRN {{.*}}, 19{{$}}
; CHECK: ret
  %base = add i32 %a, %b
  %rounded = add i32 %base, 262144
  %result = lshr i32 %rounded, 19
  ret i32 %result
}

define i32 @addurn_20(i32 %a, i32 %b) {
; CHECK-LABEL: addurn_20:
; CHECK: seal5.cv.adduRN {{.*}}, 20{{$}}
; CHECK: ret
  %base = add i32 %a, %b
  %rounded = add i32 %base, 524288
  %result = lshr i32 %rounded, 20
  ret i32 %result
}

define i32 @addurn_21(i32 %a, i32 %b) {
; CHECK-LABEL: addurn_21:
; CHECK: seal5.cv.adduRN {{.*}}, 21{{$}}
; CHECK: ret
  %base = add i32 %a, %b
  %rounded = add i32 %base, 1048576
  %result = lshr i32 %rounded, 21
  ret i32 %result
}

define i32 @addurn_22(i32 %a, i32 %b) {
; CHECK-LABEL: addurn_22:
; CHECK: seal5.cv.adduRN {{.*}}, 22{{$}}
; CHECK: ret
  %base = add i32 %a, %b
  %rounded = add i32 %base, 2097152
  %result = lshr i32 %rounded, 22
  ret i32 %result
}

define i32 @addurn_23(i32 %a, i32 %b) {
; CHECK-LABEL: addurn_23:
; CHECK: seal5.cv.adduRN {{.*}}, 23{{$}}
; CHECK: ret
  %base = add i32 %a, %b
  %rounded = add i32 %base, 4194304
  %result = lshr i32 %rounded, 23
  ret i32 %result
}

define i32 @addurn_24(i32 %a, i32 %b) {
; CHECK-LABEL: addurn_24:
; CHECK: seal5.cv.adduRN {{.*}}, 24{{$}}
; CHECK: ret
  %base = add i32 %a, %b
  %rounded = add i32 %base, 8388608
  %result = lshr i32 %rounded, 24
  ret i32 %result
}

define i32 @addurn_25(i32 %a, i32 %b) {
; CHECK-LABEL: addurn_25:
; CHECK: seal5.cv.adduRN {{.*}}, 25{{$}}
; CHECK: ret
  %base = add i32 %a, %b
  %rounded = add i32 %base, 16777216
  %result = lshr i32 %rounded, 25
  ret i32 %result
}

define i32 @addurn_26(i32 %a, i32 %b) {
; CHECK-LABEL: addurn_26:
; CHECK: seal5.cv.adduRN {{.*}}, 26{{$}}
; CHECK: ret
  %base = add i32 %a, %b
  %rounded = add i32 %base, 33554432
  %result = lshr i32 %rounded, 26
  ret i32 %result
}

define i32 @addurn_27(i32 %a, i32 %b) {
; CHECK-LABEL: addurn_27:
; CHECK: seal5.cv.adduRN {{.*}}, 27{{$}}
; CHECK: ret
  %base = add i32 %a, %b
  %rounded = add i32 %base, 67108864
  %result = lshr i32 %rounded, 27
  ret i32 %result
}

define i32 @addurn_28(i32 %a, i32 %b) {
; CHECK-LABEL: addurn_28:
; CHECK: seal5.cv.adduRN {{.*}}, 28{{$}}
; CHECK: ret
  %base = add i32 %a, %b
  %rounded = add i32 %base, 134217728
  %result = lshr i32 %rounded, 28
  ret i32 %result
}

define i32 @addurn_29(i32 %a, i32 %b) {
; CHECK-LABEL: addurn_29:
; CHECK: seal5.cv.adduRN {{.*}}, 29{{$}}
; CHECK: ret
  %base = add i32 %a, %b
  %rounded = add i32 %base, 268435456
  %result = lshr i32 %rounded, 29
  ret i32 %result
}

define i32 @addurn_30(i32 %a, i32 %b) {
; CHECK-LABEL: addurn_30:
; CHECK: seal5.cv.adduRN {{.*}}, 30{{$}}
; CHECK: ret
  %base = add i32 %a, %b
  %rounded = add i32 %base, 536870912
  %result = lshr i32 %rounded, 30
  ret i32 %result
}

define i32 @addurn_31(i32 %a, i32 %b) {
; CHECK-LABEL: addurn_31:
; CHECK: seal5.cv.adduRN {{.*}}, 31{{$}}
; CHECK: ret
  %base = add i32 %a, %b
  %rounded = add i32 %base, 1073741824
  %result = lshr i32 %rounded, 31
  ret i32 %result
}

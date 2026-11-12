; RUN: llc -O0 -mtriple=riscv32 -mattr=+m,+xcorevalu -verify-machineinstrs -global-isel=0 -global-isel-abort=1 < %s | FileCheck %s
; RUN: llc -O3 -mtriple=riscv32 -mattr=+m,+xcorevalu -verify-machineinstrs -global-isel=0 -global-isel-abort=1 < %s | FileCheck %s
; RUN: llc -O0 -mtriple=riscv32 -mattr=+m,+xcorevalu -verify-machineinstrs -global-isel=1 -global-isel-abort=1 < %s | FileCheck %s
; RUN: llc -O3 -mtriple=riscv32 -mattr=+m,+xcorevalu -verify-machineinstrs -global-isel=1 -global-isel-abort=1 < %s | FileCheck %s

define i32 @addrn_0(i32 %a, i32 %b) {
; CHECK-LABEL: addrn_0:
; CHECK: seal5.cv.add{{u?}}RN {{.*}}, 0{{$}}
; CHECK: ret
  %base = add i32 %a, %b
  ret i32 %base
}

define i32 @addrn_1(i32 %a, i32 %b) {
; CHECK-LABEL: addrn_1:
; CHECK: seal5.cv.addRN {{.*}}, 1{{$}}
; CHECK: ret
  %base = add i32 %a, %b
  %rounded = add i32 %base, 1
  %result = ashr i32 %rounded, 1
  ret i32 %result
}

define i32 @addrn_2(i32 %a, i32 %b) {
; CHECK-LABEL: addrn_2:
; CHECK: seal5.cv.addRN {{.*}}, 2{{$}}
; CHECK: ret
  %base = add i32 %a, %b
  %rounded = add i32 %base, 2
  %result = ashr i32 %rounded, 2
  ret i32 %result
}

define i32 @addrn_3(i32 %a, i32 %b) {
; CHECK-LABEL: addrn_3:
; CHECK: seal5.cv.addRN {{.*}}, 3{{$}}
; CHECK: ret
  %base = add i32 %a, %b
  %rounded = add i32 %base, 4
  %result = ashr i32 %rounded, 3
  ret i32 %result
}

define i32 @addrn_4(i32 %a, i32 %b) {
; CHECK-LABEL: addrn_4:
; CHECK: seal5.cv.addRN {{.*}}, 4{{$}}
; CHECK: ret
  %base = add i32 %a, %b
  %rounded = add i32 %base, 8
  %result = ashr i32 %rounded, 4
  ret i32 %result
}

define i32 @addrn_5(i32 %a, i32 %b) {
; CHECK-LABEL: addrn_5:
; CHECK: seal5.cv.addRN {{.*}}, 5{{$}}
; CHECK: ret
  %base = add i32 %a, %b
  %rounded = add i32 %base, 16
  %result = ashr i32 %rounded, 5
  ret i32 %result
}

define i32 @addrn_6(i32 %a, i32 %b) {
; CHECK-LABEL: addrn_6:
; CHECK: seal5.cv.addRN {{.*}}, 6{{$}}
; CHECK: ret
  %base = add i32 %a, %b
  %rounded = add i32 %base, 32
  %result = ashr i32 %rounded, 6
  ret i32 %result
}

define i32 @addrn_7(i32 %a, i32 %b) {
; CHECK-LABEL: addrn_7:
; CHECK: seal5.cv.addRN {{.*}}, 7{{$}}
; CHECK: ret
  %base = add i32 %a, %b
  %rounded = add i32 %base, 64
  %result = ashr i32 %rounded, 7
  ret i32 %result
}

define i32 @addrn_8(i32 %a, i32 %b) {
; CHECK-LABEL: addrn_8:
; CHECK: seal5.cv.addRN {{.*}}, 8{{$}}
; CHECK: ret
  %base = add i32 %a, %b
  %rounded = add i32 %base, 128
  %result = ashr i32 %rounded, 8
  ret i32 %result
}

define i32 @addrn_9(i32 %a, i32 %b) {
; CHECK-LABEL: addrn_9:
; CHECK: seal5.cv.addRN {{.*}}, 9{{$}}
; CHECK: ret
  %base = add i32 %a, %b
  %rounded = add i32 %base, 256
  %result = ashr i32 %rounded, 9
  ret i32 %result
}

define i32 @addrn_10(i32 %a, i32 %b) {
; CHECK-LABEL: addrn_10:
; CHECK: seal5.cv.addRN {{.*}}, 10{{$}}
; CHECK: ret
  %base = add i32 %a, %b
  %rounded = add i32 %base, 512
  %result = ashr i32 %rounded, 10
  ret i32 %result
}

define i32 @addrn_11(i32 %a, i32 %b) {
; CHECK-LABEL: addrn_11:
; CHECK: seal5.cv.addRN {{.*}}, 11{{$}}
; CHECK: ret
  %base = add i32 %a, %b
  %rounded = add i32 %base, 1024
  %result = ashr i32 %rounded, 11
  ret i32 %result
}

define i32 @addrn_12(i32 %a, i32 %b) {
; CHECK-LABEL: addrn_12:
; CHECK: seal5.cv.addRN {{.*}}, 12{{$}}
; CHECK: ret
  %base = add i32 %a, %b
  %rounded = add i32 %base, 2048
  %result = ashr i32 %rounded, 12
  ret i32 %result
}

define i32 @addrn_13(i32 %a, i32 %b) {
; CHECK-LABEL: addrn_13:
; CHECK: seal5.cv.addRN {{.*}}, 13{{$}}
; CHECK: ret
  %base = add i32 %a, %b
  %rounded = add i32 %base, 4096
  %result = ashr i32 %rounded, 13
  ret i32 %result
}

define i32 @addrn_14(i32 %a, i32 %b) {
; CHECK-LABEL: addrn_14:
; CHECK: seal5.cv.addRN {{.*}}, 14{{$}}
; CHECK: ret
  %base = add i32 %a, %b
  %rounded = add i32 %base, 8192
  %result = ashr i32 %rounded, 14
  ret i32 %result
}

define i32 @addrn_15(i32 %a, i32 %b) {
; CHECK-LABEL: addrn_15:
; CHECK: seal5.cv.addRN {{.*}}, 15{{$}}
; CHECK: ret
  %base = add i32 %a, %b
  %rounded = add i32 %base, 16384
  %result = ashr i32 %rounded, 15
  ret i32 %result
}

define i32 @addrn_16(i32 %a, i32 %b) {
; CHECK-LABEL: addrn_16:
; CHECK: seal5.cv.addRN {{.*}}, 16{{$}}
; CHECK: ret
  %base = add i32 %a, %b
  %rounded = add i32 %base, 32768
  %result = ashr i32 %rounded, 16
  ret i32 %result
}

define i32 @addrn_17(i32 %a, i32 %b) {
; CHECK-LABEL: addrn_17:
; CHECK: seal5.cv.addRN {{.*}}, 17{{$}}
; CHECK: ret
  %base = add i32 %a, %b
  %rounded = add i32 %base, 65536
  %result = ashr i32 %rounded, 17
  ret i32 %result
}

define i32 @addrn_18(i32 %a, i32 %b) {
; CHECK-LABEL: addrn_18:
; CHECK: seal5.cv.addRN {{.*}}, 18{{$}}
; CHECK: ret
  %base = add i32 %a, %b
  %rounded = add i32 %base, 131072
  %result = ashr i32 %rounded, 18
  ret i32 %result
}

define i32 @addrn_19(i32 %a, i32 %b) {
; CHECK-LABEL: addrn_19:
; CHECK: seal5.cv.addRN {{.*}}, 19{{$}}
; CHECK: ret
  %base = add i32 %a, %b
  %rounded = add i32 %base, 262144
  %result = ashr i32 %rounded, 19
  ret i32 %result
}

define i32 @addrn_20(i32 %a, i32 %b) {
; CHECK-LABEL: addrn_20:
; CHECK: seal5.cv.addRN {{.*}}, 20{{$}}
; CHECK: ret
  %base = add i32 %a, %b
  %rounded = add i32 %base, 524288
  %result = ashr i32 %rounded, 20
  ret i32 %result
}

define i32 @addrn_21(i32 %a, i32 %b) {
; CHECK-LABEL: addrn_21:
; CHECK: seal5.cv.addRN {{.*}}, 21{{$}}
; CHECK: ret
  %base = add i32 %a, %b
  %rounded = add i32 %base, 1048576
  %result = ashr i32 %rounded, 21
  ret i32 %result
}

define i32 @addrn_22(i32 %a, i32 %b) {
; CHECK-LABEL: addrn_22:
; CHECK: seal5.cv.addRN {{.*}}, 22{{$}}
; CHECK: ret
  %base = add i32 %a, %b
  %rounded = add i32 %base, 2097152
  %result = ashr i32 %rounded, 22
  ret i32 %result
}

define i32 @addrn_23(i32 %a, i32 %b) {
; CHECK-LABEL: addrn_23:
; CHECK: seal5.cv.addRN {{.*}}, 23{{$}}
; CHECK: ret
  %base = add i32 %a, %b
  %rounded = add i32 %base, 4194304
  %result = ashr i32 %rounded, 23
  ret i32 %result
}

define i32 @addrn_24(i32 %a, i32 %b) {
; CHECK-LABEL: addrn_24:
; CHECK: seal5.cv.addRN {{.*}}, 24{{$}}
; CHECK: ret
  %base = add i32 %a, %b
  %rounded = add i32 %base, 8388608
  %result = ashr i32 %rounded, 24
  ret i32 %result
}

define i32 @addrn_25(i32 %a, i32 %b) {
; CHECK-LABEL: addrn_25:
; CHECK: seal5.cv.addRN {{.*}}, 25{{$}}
; CHECK: ret
  %base = add i32 %a, %b
  %rounded = add i32 %base, 16777216
  %result = ashr i32 %rounded, 25
  ret i32 %result
}

define i32 @addrn_26(i32 %a, i32 %b) {
; CHECK-LABEL: addrn_26:
; CHECK: seal5.cv.addRN {{.*}}, 26{{$}}
; CHECK: ret
  %base = add i32 %a, %b
  %rounded = add i32 %base, 33554432
  %result = ashr i32 %rounded, 26
  ret i32 %result
}

define i32 @addrn_27(i32 %a, i32 %b) {
; CHECK-LABEL: addrn_27:
; CHECK: seal5.cv.addRN {{.*}}, 27{{$}}
; CHECK: ret
  %base = add i32 %a, %b
  %rounded = add i32 %base, 67108864
  %result = ashr i32 %rounded, 27
  ret i32 %result
}

define i32 @addrn_28(i32 %a, i32 %b) {
; CHECK-LABEL: addrn_28:
; CHECK: seal5.cv.addRN {{.*}}, 28{{$}}
; CHECK: ret
  %base = add i32 %a, %b
  %rounded = add i32 %base, 134217728
  %result = ashr i32 %rounded, 28
  ret i32 %result
}

define i32 @addrn_29(i32 %a, i32 %b) {
; CHECK-LABEL: addrn_29:
; CHECK: seal5.cv.addRN {{.*}}, 29{{$}}
; CHECK: ret
  %base = add i32 %a, %b
  %rounded = add i32 %base, 268435456
  %result = ashr i32 %rounded, 29
  ret i32 %result
}

define i32 @addrn_30(i32 %a, i32 %b) {
; CHECK-LABEL: addrn_30:
; CHECK: seal5.cv.addRN {{.*}}, 30{{$}}
; CHECK: ret
  %base = add i32 %a, %b
  %rounded = add i32 %base, 536870912
  %result = ashr i32 %rounded, 30
  ret i32 %result
}

define i32 @addrn_31(i32 %a, i32 %b) {
; CHECK-LABEL: addrn_31:
; CHECK: seal5.cv.addRN {{.*}}, 31{{$}}
; CHECK: ret
  %base = add i32 %a, %b
  %rounded = add i32 %base, 1073741824
  %result = ashr i32 %rounded, 31
  ret i32 %result
}

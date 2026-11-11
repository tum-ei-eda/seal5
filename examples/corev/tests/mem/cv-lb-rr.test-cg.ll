; RUN: llc -mtriple=riscv32 -mattr=+m,+xcorevmem -verify-machineinstrs %s -o - | FileCheck %s
; RUN: llc -mtriple=riscv32 -mattr=+m,+xcorevmem -global-isel=1 -global-isel-abort=1 -verify-machineinstrs %s -o - | FileCheck %s

define i32 @lb_register_offset(ptr %base, i32 %offset) {
; CHECK-LABEL: lb_register_offset:
; CHECK: seal5.cv.lb
  %address = getelementptr i8, ptr %base, i32 %offset
  %value = load i8, ptr %address, align 1
  %extended = sext i8 %value to i32
  ret i32 %extended
}

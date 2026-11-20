; RUN: llc -mtriple=riscv32 -mattr=+m,+xcorevmem -verify-machineinstrs %s -o - | FileCheck %s
; RUN: llc -mtriple=riscv32 -mattr=+m,+xcorevmem -global-isel=1 -global-isel-abort=1 -verify-machineinstrs %s -o - | FileCheck %s

define i32 @lbu_register_offset(ptr %base, i32 %offset) {
; CHECK-LABEL: lbu_register_offset:
; CHECK: seal5.cv.lbu
  %address = getelementptr i8, ptr %base, i32 %offset
  %value = load i8, ptr %address, align 1
  %extended = zext i8 %value to i32
  ret i32 %extended
}

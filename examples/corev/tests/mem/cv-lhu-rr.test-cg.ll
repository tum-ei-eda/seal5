; RUN: llc -mtriple=riscv32 -mattr=+m,+xcorevmem -verify-machineinstrs %s -o - | FileCheck %s
; RUN: llc -mtriple=riscv32 -mattr=+m,+xcorevmem -global-isel=1 -global-isel-abort=1 -verify-machineinstrs %s -o - | FileCheck %s

define i32 @lhu_register_offset(ptr %base, i32 %offset) {
; CHECK-LABEL: lhu_register_offset:
; CHECK: seal5.cv.lhu
  %address = getelementptr i8, ptr %base, i32 %offset
  %value = load i16, ptr %address, align 2
  %extended = zext i16 %value to i32
  ret i32 %extended
}

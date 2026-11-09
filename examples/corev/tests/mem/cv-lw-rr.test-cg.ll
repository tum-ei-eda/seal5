; RUN: llc -mtriple=riscv32 -mattr=+m,+xcorevmem -verify-machineinstrs %s -o - | FileCheck %s
; RUN: llc -mtriple=riscv32 -mattr=+m,+xcorevmem -global-isel=1 -global-isel-abort=1 -verify-machineinstrs %s -o - | FileCheck %s

define i32 @lw_register_offset(ptr %base, i32 %offset) {
; CHECK-LABEL: lw_register_offset:
; CHECK: seal5.cv.lw
  %address = getelementptr i8, ptr %base, i32 %offset
  %value = load i32, ptr %address, align 4
  ret i32 %value
}

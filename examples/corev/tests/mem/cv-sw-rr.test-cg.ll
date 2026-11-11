; RUN: llc -mtriple=riscv32 -mattr=+m,+xcorevmem -verify-machineinstrs %s -o - | FileCheck %s
; RUN: llc -mtriple=riscv32 -mattr=+m,+xcorevmem -global-isel=1 -global-isel-abort=1 -verify-machineinstrs %s -o - | FileCheck %s

define void @sw_register_offset(ptr %base, i32 %offset, i32 %value) {
; CHECK-LABEL: sw_register_offset:
; CHECK: seal5.cv.sw
  %address = getelementptr i8, ptr %base, i32 %offset
  store i32 %value, ptr %address, align 4
  ret void
}

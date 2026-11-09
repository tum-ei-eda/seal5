; RUN: llc -mtriple=riscv32 -mattr=+m,+xcorevmem -verify-machineinstrs %s -o - | FileCheck %s
; RUN: llc -mtriple=riscv32 -mattr=+m,+xcorevmem -global-isel=1 -global-isel-abort=1 -verify-machineinstrs %s -o - | FileCheck %s

define void @sb_register_offset(ptr %base, i32 %offset, i32 %value) {
; CHECK-LABEL: sb_register_offset:
; CHECK: seal5.cv.sb
  %address = getelementptr i8, ptr %base, i32 %offset
  %narrow = trunc i32 %value to i8
  store i8 %narrow, ptr %address, align 1
  ret void
}

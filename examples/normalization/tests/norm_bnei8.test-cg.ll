; RUN: llc -O2 -mtriple=riscv32 -mattr=+xnormalize32 -verify-machineinstrs -global-isel=1 -global-isel-abort=1 < %s | FileCheck %s
; RUN: llc -O2 -mtriple=riscv32 -mattr=+xnormalize32 -verify-machineinstrs -global-isel=1 -global-isel-abort=1 -filetype=obj < %s -o %t.o
; RUN: llvm-objdump -d --mattr=+xnormalize32 %t.o | FileCheck %s --check-prefix=OBJ

@branch_fall = external global i8
@branch_taken = external global i8

define void @signed8_min(i32 %value) {
; OBJ-LABEL: <signed8_min>:
; OBJ: xnormalize32.bnei8
; CHECK-LABEL: signed8_min:
; CHECK: xnormalize32.bnei8 a0, -128,
  %condition = icmp ne i32 %value, -128
  br i1 %condition, label %taken, label %fall
fall:
  store volatile i8 1, ptr @branch_fall
  ret void
taken:
  store volatile i8 2, ptr @branch_taken
  ret void
}

define void @signed8_max(i32 %value) {
; OBJ-LABEL: <signed8_max>:
; OBJ: xnormalize32.bnei8
; CHECK-LABEL: signed8_max:
; CHECK: xnormalize32.bnei8 a0, 127,
  %condition = icmp ne i32 %value, 127
  br i1 %condition, label %taken, label %fall
fall:
  store volatile i8 1, ptr @branch_fall
  ret void
taken:
  store volatile i8 2, ptr @branch_taken
  ret void
}

; RUN: llc -O2 -mtriple=riscv32 -mattr=+xnormalize32 -verify-machineinstrs -global-isel=1 -global-isel-abort=1 < %s | FileCheck %s
; RUN: llc -O2 -mtriple=riscv32 -mattr=+xnormalize32 -verify-machineinstrs -global-isel=1 -global-isel-abort=1 -filetype=obj < %s -o %t.o
; RUN: llvm-objdump -d --mattr=+xnormalize32 %t.o | FileCheck %s --check-prefix=OBJ

@branch_fall = external global i8
@branch_taken = external global i8

define void @signed5_min(i32 %value) {
; CHECK-LABEL: signed5_min:
; CHECK: xnormalize32.beqi5 a0, -16,
; OBJ-LABEL: <signed5_min>:
; OBJ: xnormalize32.beqi5
  %condition = icmp eq i32 %value, -16
  br i1 %condition, label %taken, label %fall
fall:
  store volatile i8 1, ptr @branch_fall
  ret void
taken:
  store volatile i8 2, ptr @branch_taken
  ret void
}

define void @signed5_max(i32 %value) {
; OBJ-LABEL: <signed5_max>:
; OBJ: xnormalize32.beqi5
; CHECK-LABEL: signed5_max:
; CHECK: xnormalize32.beqi5 a0, 15,
  %condition = icmp eq i32 %value, 15
  br i1 %condition, label %taken, label %fall
fall:
  store volatile i8 1, ptr @branch_fall
  ret void
taken:
  store volatile i8 2, ptr @branch_taken
  ret void
}

define void @signed5_too_large(i32 %value) {
; CHECK-LABEL: signed5_too_large:
; CHECK-NOT: xnormalize32.beqi5
; CHECK: ret
  %condition = icmp eq i32 %value, 16
  br i1 %condition, label %taken, label %fall
fall:
  store volatile i8 1, ptr @branch_fall
  ret void
taken:
  store volatile i8 2, ptr @branch_taken
  ret void
}

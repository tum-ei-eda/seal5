; RUN: llc -O2 -mtriple=riscv32 -mattr=+xnormalize32 -verify-machineinstrs -global-isel=1 -global-isel-abort=1 < %s | FileCheck %s
; RUN: llc -O2 -mtriple=riscv32 -mattr=+xnormalize32 -verify-machineinstrs -global-isel=1 -global-isel-abort=1 -filetype=obj < %s -o %t.o
; RUN: llvm-objdump -d --mattr=+xnormalize32 %t.o | FileCheck %s --check-prefix=OBJ

@branch_fall = external global i8
@branch_taken = external global i8

define void @branch_equal(i32 %a, i32 %b) {
; CHECK-LABEL: branch_equal:
; CHECK: xnormalize32.branch
; OBJ-LABEL: <branch_equal>:
; OBJ: xnormalize32.branch
  %eq = icmp eq i32 %a, %b
  br i1 %eq, label %yes, label %no
no:
  store volatile i8 1, ptr @branch_fall
  ret void
yes:
  store volatile i8 2, ptr @branch_taken
  ret void
}

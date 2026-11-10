; RUN: llc -O2 -mtriple=riscv32 -mattr=+xnormalize32 -verify-machineinstrs -global-isel=1 -global-isel-abort=1 < %s | FileCheck %s
; RUN: llc -O2 -mtriple=riscv32 -mattr=+xnormalize32 -verify-machineinstrs -global-isel=1 -global-isel-abort=1 -filetype=obj < %s -o %t.o
; RUN: llvm-objdump -d --mattr=+xnormalize32 %t.o | FileCheck %s --check-prefix=OBJ

@branch_fall = external global i8
@branch_taken = external global i8

; XOR-nonzero canonicalizes to register inequality.

define void @bxor(i32 %a, i32 %b) {
; CHECK-LABEL: bxor:
; CHECK: xnormalize32.bxor
; OBJ-LABEL: <bxor>:
; OBJ: xnormalize32.bxor

  %c = icmp ne i32 %a, %b
  br i1 %c, label %taken, label %fall
fall:
  store volatile i8 1, ptr @branch_fall
  ret void
taken:
  store volatile i8 2, ptr @branch_taken
  ret void
}

; RUN: llc -O2 -mtriple=riscv64 -mattr=+xnormalize64 -verify-machineinstrs -global-isel=1 -global-isel-abort=1 < %s | FileCheck %s
; RUN: llc -O2 -mtriple=riscv64 -mattr=+xnormalize64 -verify-machineinstrs -global-isel=1 -global-isel-abort=1 -filetype=obj < %s -o %t.o
; RUN: llvm-objdump -d --mattr=+xnormalize64 %t.o | FileCheck %s --check-prefix=OBJ

define void @signed64_bound(i64 %value) {
; CHECK-LABEL: signed64_bound:
; CHECK: xnormalize64.blti5 a0, -16,
; OBJ-LABEL: <signed64_bound>:
; OBJ: xnormalize64.blti5
  %condition = icmp slt i64 %value, -16
  br i1 %condition, label %taken, label %fall
fall:
  call void asm sideeffect "addi zero, zero, 1", ""()
  ret void
taken:
  call void asm sideeffect "nop", ""()
  ret void
}

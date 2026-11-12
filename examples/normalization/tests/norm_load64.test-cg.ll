; RUN: llc -O2 -mtriple=riscv64 -mattr=+xnormalize64 -verify-machineinstrs -global-isel=1 -global-isel-abort=1 < %s | FileCheck %s
; RUN: llc -O2 -mtriple=riscv64 -mattr=+xnormalize64 -verify-machineinstrs -global-isel=1 -global-isel-abort=1 -filetype=obj < %s -o %t.o
; RUN: llvm-objdump -d --mattr=+xnormalize64 %t.o | FileCheck %s --check-prefix=OBJ

define i64 @load64(ptr %p) {
; OBJ-LABEL: <load64>:
; OBJ: xnormalize64.load64
; CHECK-LABEL: load64:
; CHECK: xnormalize64.load64 a0, a0
  %v = load i64, ptr %p, align 8
  ret i64 %v
}

; RUN: llc -O2 -mtriple=riscv64 -mattr=+xnormalize64 -verify-machineinstrs -global-isel=1 -global-isel-abort=1 < %s | FileCheck %s
; RUN: llc -O2 -mtriple=riscv64 -mattr=+xnormalize64 -verify-machineinstrs -global-isel=1 -global-isel-abort=1 -filetype=obj < %s -o %t.o
; RUN: llvm-objdump -d --mattr=+xnormalize64 %t.o | FileCheck %s --check-prefix=OBJ

define i64 @load32(ptr %p) {
; OBJ-LABEL: <load32>:
; OBJ: xnormalize64.load32
; CHECK-LABEL: load32:
; CHECK: xnormalize64.load32 a0, a0
  %v = load i32, ptr %p, align 4
  %r = zext i32 %v to i64
  ret i64 %r
}

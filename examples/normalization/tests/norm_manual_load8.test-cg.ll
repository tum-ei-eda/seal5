; RUN: llc -O2 -mtriple=riscv32 -mattr=+xnormalize32 -verify-machineinstrs -global-isel=1 -global-isel-abort=1 < %s | FileCheck %s
; RUN: llc -O2 -mtriple=riscv32 -mattr=+xnormalize32 -verify-machineinstrs -global-isel=1 -global-isel-abort=1 -filetype=obj < %s -o %t.o
; RUN: llvm-objdump -d --mattr=+xnormalize32 %t.o | FileCheck %s --check-prefix=OBJ

define i32 @load8(ptr %p) {
; OBJ-LABEL: <load8>:
; OBJ: xnormalize32.load8
; CHECK-LABEL: load8:
; CHECK: xnormalize32.load8 a0, a0
  %v = load i8, ptr %p, align 1
  %r = zext i8 %v to i32
  ret i32 %r
}

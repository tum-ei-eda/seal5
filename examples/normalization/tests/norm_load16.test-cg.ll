; RUN: llc -O2 -mtriple=riscv32 -mattr=+xnormalize32 -verify-machineinstrs -global-isel=1 -global-isel-abort=1 < %s | FileCheck %s
; RUN: llc -O2 -mtriple=riscv32 -mattr=+xnormalize32 -verify-machineinstrs -global-isel=1 -global-isel-abort=1 -filetype=obj < %s -o %t.o
; RUN: llvm-objdump -d --mattr=+xnormalize32 %t.o | FileCheck %s --check-prefix=OBJ

define i32 @load16(ptr %p) {
; OBJ-LABEL: <load16>:
; OBJ: xnormalize32.load16
; CHECK-LABEL: load16:
; CHECK: xnormalize32.load16 a0, a0
  %v = load i16, ptr %p, align 2
  %r = zext i16 %v to i32
  ret i32 %r
}

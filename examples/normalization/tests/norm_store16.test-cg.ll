; RUN: llc -O2 -mtriple=riscv32 -mattr=+xnormalize32 -verify-machineinstrs -global-isel=1 -global-isel-abort=1 < %s | FileCheck %s
; RUN: llc -O2 -mtriple=riscv32 -mattr=+xnormalize32 -verify-machineinstrs -global-isel=1 -global-isel-abort=1 -filetype=obj < %s -o %t.o
; RUN: llvm-objdump -d --mattr=+xnormalize32 %t.o | FileCheck %s --check-prefix=OBJ

define void @store16(ptr %p, i32 %v) {
; OBJ-LABEL: <store16>:
; OBJ: xnormalize32.store16
; CHECK-LABEL: store16:
; CHECK: xnormalize32.store16 a1, a0
  %short = trunc i32 %v to i16
  store i16 %short, ptr %p, align 2
  ret void
}

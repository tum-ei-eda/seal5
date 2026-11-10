; RUN: llc -O2 -mtriple=riscv32 -mattr=+xnormalize32 -verify-machineinstrs -global-isel=1 -global-isel-abort=1 < %s | FileCheck %s
; RUN: llc -O2 -mtriple=riscv32 -mattr=+xnormalize32 -verify-machineinstrs -global-isel=1 -global-isel-abort=1 -filetype=obj < %s -o %t.o
; RUN: llvm-objdump -d --mattr=+xnormalize32 %t.o | FileCheck %s --check-prefix=OBJ

define i32 @loadx(ptr %p) {
; OBJ-LABEL: <loadx>:
; OBJ: xnormalize32.loadx
; CHECK-LABEL: loadx:
; CHECK: xnormalize32.loadx a0, a0
  %v = load i32, ptr %p, align 4
  ret i32 %v
}

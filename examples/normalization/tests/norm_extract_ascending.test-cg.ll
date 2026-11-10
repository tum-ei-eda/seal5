; RUN: llc -O2 -mtriple=riscv32 -mattr=+xnormalize32 -verify-machineinstrs -global-isel=1 -global-isel-abort=1 < %s | FileCheck %s
; RUN: llc -O2 -mtriple=riscv32 -mattr=+xnormalize32 -verify-machineinstrs -global-isel=1 -global-isel-abort=1 -filetype=obj < %s -o %t.o
; RUN: llvm-objdump -d --mattr=+xnormalize32 %t.o | FileCheck %s --check-prefix=OBJ

define i32 @extract4(i32 %value) {
; OBJ-LABEL: <extract4>:
; OBJ: xnormalize32.extract4
; CHECK-LABEL: extract4:
; CHECK: xnormalize32.extract4 a0, a0, 8
  %shift = lshr i32 %value, 8
  %result = and i32 %shift, 15
  ret i32 %result
}

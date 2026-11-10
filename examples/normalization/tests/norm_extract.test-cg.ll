; RUN: llc -O2 -mtriple=riscv32 -mattr=+xnormalize32 -verify-machineinstrs -global-isel=1 -global-isel-abort=1 < %s | FileCheck %s
; RUN: llc -O2 -mtriple=riscv32 -mattr=+xnormalize32 -verify-machineinstrs -global-isel=1 -global-isel-abort=1 -filetype=obj < %s -o %t.o
; RUN: llvm-objdump -d --mattr=+xnormalize32 %t.o | FileCheck %s --check-prefix=OBJ

define i32 @extract8(i32 %value) {
; OBJ-LABEL: <extract8>:
; OBJ: xnormalize32.extract
; CHECK-LABEL: extract8:
; CHECK: xnormalize32.extract a0, a0, 8
  %shift = lshr i32 %value, 8
  %result = and i32 %shift, 255
  ret i32 %result
}

define i32 @extract8_unaligned(i32 %value) {
; OBJ-LABEL: <extract8_unaligned>:
; OBJ: xnormalize32.extract
; CHECK-LABEL: extract8_unaligned:
; CHECK: xnormalize32.extract a0, a0, 3
  %shift = lshr i32 %value, 3
  %result = and i32 %shift, 255
  ret i32 %result
}

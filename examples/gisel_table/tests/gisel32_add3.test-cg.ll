; RUN: llc -O2 -mtriple=riscv32 -mattr=+xgiseltable32 -global-isel=1 -global-isel-abort=1 -verify-machineinstrs < %s | FileCheck %s
; RUN: llc -O2 -mtriple=riscv32 -mattr=+xgiseltable32 -global-isel=1 -global-isel-abort=1 -verify-machineinstrs -filetype=obj < %s -o %t.o
; RUN: llvm-objdump -d --mattr=+xgiseltable32 %t.o | FileCheck %s --check-prefix=OBJ
; RUN: llc -O2 -mtriple=riscv32 -global-isel=1 -global-isel-abort=1 -verify-machineinstrs < %s | FileCheck %s --check-prefix=NATIVE

define i32 @add3(i32 %a, i32 %b, i32 %c) {
; CHECK-LABEL: add3:
; CHECK: xgiseltable32.add3
; OBJ-LABEL: <add3>:
; OBJ: xgiseltable32.add3
; NATIVE-LABEL: add3:
; NATIVE-NOT: xgiseltable
; NATIVE: ret
  %ab = add i32 %a, %b
  %r = add i32 %ab, %c
  ret i32 %r
}

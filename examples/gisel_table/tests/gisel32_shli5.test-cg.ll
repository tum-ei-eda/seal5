; RUN: llc -O2 -mtriple=riscv32 -mattr=+xgiseltable32 -global-isel=1 -global-isel-abort=1 -verify-machineinstrs < %s | FileCheck %s
; RUN: llc -O2 -mtriple=riscv32 -mattr=+xgiseltable32 -global-isel=1 -global-isel-abort=1 -verify-machineinstrs -filetype=obj < %s -o %t.o
; RUN: llvm-objdump -d --mattr=+xgiseltable32 %t.o | FileCheck %s --check-prefix=OBJ
; RUN: llc -O2 -mtriple=riscv32 -global-isel=1 -global-isel-abort=1 -verify-machineinstrs < %s | FileCheck %s --check-prefix=NATIVE

define i32 @shli5(i32 %a) {
; CHECK-LABEL: shli5:
; CHECK: xgiseltable32.shli5
; OBJ-LABEL: <shli5>:
; OBJ: xgiseltable32.shli5
; NATIVE-LABEL: shli5:
; NATIVE-NOT: xgiseltable
; NATIVE: ret
  %r = shl i32 %a, 31
  ret i32 %r
}

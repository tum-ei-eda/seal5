; RUN: llc -O2 -mtriple=riscv32 -mattr=+xgiseltable32 -global-isel=1 -global-isel-abort=1 -verify-machineinstrs < %s | FileCheck %s
; RUN: llc -O2 -mtriple=riscv32 -mattr=+xgiseltable32 -global-isel=1 -global-isel-abort=1 -verify-machineinstrs -filetype=obj < %s -o %t.o
; RUN: llvm-objdump -d --mattr=+xgiseltable32 %t.o | FileCheck %s --check-prefix=OBJ
; RUN: llc -O2 -mtriple=riscv32 -global-isel=1 -global-isel-abort=1 -verify-machineinstrs < %s | FileCheck %s --check-prefix=NATIVE

define i32 @subincacc(i32 %acc, i32 %a, i32 %b) {
; CHECK-LABEL: subincacc:
; CHECK: xgiseltable32.subincacc
; OBJ-LABEL: <subincacc>:
; OBJ: xgiseltable32.subincacc
; NATIVE-LABEL: subincacc:
; NATIVE-NOT: xgiseltable
; NATIVE: ret
  %inc = add i32 %a, 1
  %sub = sub i32 %inc, %b
  %r = add i32 %sub, %acc
  ret i32 %r
}

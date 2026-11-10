; RUN: llc -O2 -mtriple=riscv64 -mattr=+xgiseltable64 -global-isel=1 -global-isel-abort=1 -verify-machineinstrs < %s | FileCheck %s
; RUN: llc -O2 -mtriple=riscv64 -mattr=+xgiseltable64 -global-isel=1 -global-isel-abort=1 -verify-machineinstrs -filetype=obj < %s -o %t.o
; RUN: llvm-objdump -d --mattr=+xgiseltable64 %t.o | FileCheck %s --check-prefix=OBJ
; RUN: llc -O2 -mtriple=riscv64 -global-isel=1 -global-isel-abort=1 -verify-machineinstrs < %s | FileCheck %s --check-prefix=NATIVE

define i64 @add3(i64 %a, i64 %b, i64 %c) {
; CHECK-LABEL: add3:
; CHECK: xgiseltable64.add3
; OBJ-LABEL: <add3>:
; OBJ: xgiseltable64.add3
; NATIVE-LABEL: add3:
; NATIVE-NOT: xgiseltable
; NATIVE: ret
  %ab = add i64 %a, %b
  %r = add i64 %ab, %c
  ret i64 %r
}

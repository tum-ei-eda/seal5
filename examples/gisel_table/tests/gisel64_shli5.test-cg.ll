; RUN: llc -O2 -mtriple=riscv64 -mattr=+xgiseltable64 -global-isel=1 -global-isel-abort=1 -verify-machineinstrs < %s | FileCheck %s
; RUN: llc -O2 -mtriple=riscv64 -mattr=+xgiseltable64 -global-isel=1 -global-isel-abort=1 -verify-machineinstrs -filetype=obj < %s -o %t.o
; RUN: llvm-objdump -d --mattr=+xgiseltable64 %t.o | FileCheck %s --check-prefix=OBJ
; RUN: llc -O2 -mtriple=riscv64 -global-isel=1 -global-isel-abort=1 -verify-machineinstrs < %s | FileCheck %s --check-prefix=NATIVE

define i64 @shli5(i64 %a) {
; CHECK-LABEL: shli5:
; CHECK: xgiseltable64.shli5
; OBJ-LABEL: <shli5>:
; OBJ: xgiseltable64.shli5
; NATIVE-LABEL: shli5:
; NATIVE-NOT: xgiseltable
; NATIVE: ret
  %r = shl i64 %a, 31
  ret i64 %r
}

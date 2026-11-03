; RUN: llc -O2 -mtriple=riscv64 -mattr=+xgiseltable64 -global-isel=1 -global-isel-abort=1 -verify-machineinstrs < %s | FileCheck %s
; RUN: llc -O2 -mtriple=riscv64 -mattr=+xgiseltable64 -global-isel=1 -global-isel-abort=1 -verify-machineinstrs -filetype=obj < %s -o %t.o
; RUN: llvm-objdump -d --mattr=+xgiseltable64 %t.o | FileCheck %s --check-prefix=OBJ
; RUN: llc -O2 -mtriple=riscv64 -global-isel=1 -global-isel-abort=1 -verify-machineinstrs < %s | FileCheck %s --check-prefix=NATIVE

define i64 @subincacc(i64 %acc, i64 %a, i64 %b) {
; CHECK-LABEL: subincacc:
; CHECK: xgiseltable64.subincacc
; OBJ-LABEL: <subincacc>:
; OBJ: xgiseltable64.subincacc
; NATIVE-LABEL: subincacc:
; NATIVE-NOT: xgiseltable
; NATIVE: ret
  %inc = add i64 %a, 1
  %sub = sub i64 %inc, %b
  %r = add i64 %sub, %acc
  ret i64 %r
}

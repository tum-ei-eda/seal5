; RUN: llc -O2 -mtriple=riscv64 -mattr=+xgiseltable64 -global-isel=1 -global-isel-abort=1 -verify-machineinstrs < %s | FileCheck %s
; RUN: llc -O2 -mtriple=riscv64 -mattr=+xgiseltable64 -global-isel=1 -global-isel-abort=1 -verify-machineinstrs -filetype=obj < %s -o %t.o
; RUN: llvm-objdump -d --mattr=+xgiseltable64 %t.o | FileCheck %s --check-prefix=OBJ
; RUN: llc -O2 -mtriple=riscv64 -global-isel=1 -global-isel-abort=1 -verify-machineinstrs < %s | FileCheck %s --check-prefix=NATIVE


define {i64, i64} @sumdiff(i64 %a, i64 %b) {
; CHECK-LABEL: sumdiff:
; CHECK: xgiseltable64.sumdiff
; OBJ-LABEL: <sumdiff>:
; OBJ: xgiseltable64.sumdiff
; NATIVE-LABEL: sumdiff:
; NATIVE-NOT: xgiseltable
; NATIVE: ret
  %sum = add i64 %a, %b
  %diff = sub i64 %a, %b
  %first = insertvalue {i64, i64} poison, i64 %sum, 0
  %both = insertvalue {i64, i64} %first, i64 %diff, 1
  ret {i64, i64} %both
}

define {i64, i64} @diffsum(i64 %a, i64 %b) {
; CHECK-LABEL: diffsum:
; CHECK: xgiseltable64.sumdiff
; OBJ-LABEL: <diffsum>:
; OBJ: xgiseltable64.sumdiff
; NATIVE-LABEL: diffsum:
; NATIVE-NOT: xgiseltable
; NATIVE: ret
  %diff = sub i64 %a, %b
  %sum = add i64 %a, %b
  %first = insertvalue {i64, i64} poison, i64 %sum, 0
  %both = insertvalue {i64, i64} %first, i64 %diff, 1
  ret {i64, i64} %both
}

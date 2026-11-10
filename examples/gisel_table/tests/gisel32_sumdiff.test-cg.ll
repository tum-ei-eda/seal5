; RUN: llc -O2 -mtriple=riscv32 -mattr=+xgiseltable32 -global-isel=1 -global-isel-abort=1 -verify-machineinstrs < %s | FileCheck %s
; RUN: llc -O2 -mtriple=riscv32 -mattr=+xgiseltable32 -global-isel=1 -global-isel-abort=1 -verify-machineinstrs -filetype=obj < %s -o %t.o
; RUN: llvm-objdump -d --mattr=+xgiseltable32 %t.o | FileCheck %s --check-prefix=OBJ
; RUN: llc -O2 -mtriple=riscv32 -global-isel=1 -global-isel-abort=1 -verify-machineinstrs < %s | FileCheck %s --check-prefix=NATIVE


define {i32, i32} @sumdiff(i32 %a, i32 %b) {
; CHECK-LABEL: sumdiff:
; CHECK: xgiseltable32.sumdiff
; OBJ-LABEL: <sumdiff>:
; OBJ: xgiseltable32.sumdiff
; NATIVE-LABEL: sumdiff:
; NATIVE-NOT: xgiseltable
; NATIVE: ret
  %sum = add i32 %a, %b
  %diff = sub i32 %a, %b
  %first = insertvalue {i32, i32} poison, i32 %sum, 0
  %both = insertvalue {i32, i32} %first, i32 %diff, 1
  ret {i32, i32} %both
}

define {i32, i32} @diffsum(i32 %a, i32 %b) {
; CHECK-LABEL: diffsum:
; CHECK: xgiseltable32.sumdiff
; OBJ-LABEL: <diffsum>:
; OBJ: xgiseltable32.sumdiff
; NATIVE-LABEL: diffsum:
; NATIVE-NOT: xgiseltable
; NATIVE: ret
  %diff = sub i32 %a, %b
  %sum = add i32 %a, %b
  %first = insertvalue {i32, i32} poison, i32 %sum, 0
  %both = insertvalue {i32, i32} %first, i32 %diff, 1
  ret {i32, i32} %both
}

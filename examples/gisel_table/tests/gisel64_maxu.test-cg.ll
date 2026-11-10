; RUN: llc -O2 -mtriple=riscv64 -mattr=+xgiseltable64 -global-isel=1 -global-isel-abort=1 -verify-machineinstrs < %s | FileCheck %s
; RUN: llc -O2 -mtriple=riscv64 -mattr=+xgiseltable64 -global-isel=1 -global-isel-abort=1 -verify-machineinstrs -filetype=obj < %s -o %t.o
; RUN: llvm-objdump -d --mattr=+xgiseltable64 %t.o | FileCheck %s --check-prefix=OBJ
; RUN: llc -O2 -mtriple=riscv64 -global-isel=1 -global-isel-abort=1 -verify-machineinstrs < %s | FileCheck %s --check-prefix=NATIVE

define i64 @maxu(i64 %a, i64 %b) {
; CHECK-LABEL: maxu:
; CHECK: xgiseltable64.maxu
; OBJ-LABEL: <maxu>:
; OBJ: xgiseltable64.maxu
; NATIVE-LABEL: maxu:
; NATIVE-NOT: xgiseltable
; NATIVE: ret
  %r = call i64 @llvm.umax.i64(i64 %a, i64 %b)
  ret i64 %r
}

declare i64 @llvm.umax.i64(i64, i64)

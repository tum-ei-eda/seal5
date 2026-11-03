; RUN: llc -O2 -mtriple=riscv32 -mattr=+xgiseltable32 -global-isel=1 -global-isel-abort=1 -verify-machineinstrs < %s | FileCheck %s
; RUN: llc -O2 -mtriple=riscv32 -mattr=+xgiseltable32 -global-isel=1 -global-isel-abort=1 -verify-machineinstrs -filetype=obj < %s -o %t.o
; RUN: llvm-objdump -d --mattr=+xgiseltable32 %t.o | FileCheck %s --check-prefix=OBJ
; RUN: llc -O2 -mtriple=riscv32 -global-isel=1 -global-isel-abort=1 -verify-machineinstrs < %s | FileCheck %s --check-prefix=NATIVE

define i32 @maxu(i32 %a, i32 %b) {
; CHECK-LABEL: maxu:
; CHECK: xgiseltable32.maxu
; OBJ-LABEL: <maxu>:
; OBJ: xgiseltable32.maxu
; NATIVE-LABEL: maxu:
; NATIVE-NOT: xgiseltable
; NATIVE: ret
  %r = call i32 @llvm.umax.i32(i32 %a, i32 %b)
  ret i32 %r
}

declare i32 @llvm.umax.i32(i32, i32)

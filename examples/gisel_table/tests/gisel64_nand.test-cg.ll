; RUN: llc -O2 -mtriple=riscv64 -mattr=+xgiseltable64 -global-isel=1 -global-isel-abort=1 -verify-machineinstrs < %s | FileCheck %s
; RUN: llc -O2 -mtriple=riscv64 -mattr=+xgiseltable64 -global-isel=1 -global-isel-abort=1 -verify-machineinstrs -filetype=obj < %s -o %t.o
; RUN: llvm-objdump -d --mattr=+xgiseltable64 %t.o | FileCheck %s --check-prefix=OBJ
; RUN: llc -O2 -mtriple=riscv64 -global-isel=1 -global-isel-abort=1 -verify-machineinstrs < %s | FileCheck %s --check-prefix=NATIVE

define i64 @nand(i64 %a, i64 %b) {
; CHECK-LABEL: nand:
; CHECK: xgiseltable64.nand
; OBJ-LABEL: <nand>:
; OBJ: xgiseltable64.nand
; NATIVE-LABEL: nand:
; NATIVE-NOT: xgiseltable
; NATIVE: ret
  %and = and i64 %a, %b
  %r = xor i64 %and, -1
  ret i64 %r
}

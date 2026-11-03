; RUN: llc -O2 -mtriple=riscv32 -mattr=+xgiseltable32 -global-isel=1 -global-isel-abort=1 -verify-machineinstrs < %s | FileCheck %s
; RUN: llc -O2 -mtriple=riscv32 -mattr=+xgiseltable32 -global-isel=1 -global-isel-abort=1 -verify-machineinstrs -filetype=obj < %s -o %t.o
; RUN: llvm-objdump -d --mattr=+xgiseltable32 %t.o | FileCheck %s --check-prefix=OBJ
; RUN: llc -O2 -mtriple=riscv32 -global-isel=1 -global-isel-abort=1 -verify-machineinstrs < %s | FileCheck %s --check-prefix=NATIVE

define i32 @nand(i32 %a, i32 %b) {
; CHECK-LABEL: nand:
; CHECK: xgiseltable32.nand
; OBJ-LABEL: <nand>:
; OBJ: xgiseltable32.nand
; NATIVE-LABEL: nand:
; NATIVE-NOT: xgiseltable
; NATIVE: ret
  %and = and i32 %a, %b
  %r = xor i32 %and, -1
  ret i32 %r
}

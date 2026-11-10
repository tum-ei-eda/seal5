; RUN: llc -O2 -mtriple=riscv64 -mattr=+xnormalize64 -verify-machineinstrs -global-isel=1 -global-isel-abort=1 < %s | FileCheck %s
; RUN: llc -O2 -mtriple=riscv64 -mattr=+xnormalize64 -verify-machineinstrs -global-isel=1 -global-isel-abort=1 -filetype=obj < %s -o %t.o
; RUN: llvm-objdump -d --mattr=+xnormalize64 %t.o | FileCheck %s --check-prefix=OBJ
; RUN: llc -O2 -mtriple=riscv64 -verify-machineinstrs -global-isel=1 -global-isel-abort=1 < %s | FileCheck %s --check-prefix=NATIVE

define i64 @ldx_reg(ptr %base, i64 %index) {
; CHECK-LABEL: ldx_reg:
; CHECK: xnormalize64.ldx.reg a0, a1, a0
; CHECK-NEXT: ret
; OBJ-LABEL: <ldx_reg>:
; OBJ: xnormalize64.ldx.reg
; NATIVE-LABEL: ldx_reg:
; NATIVE-NOT: xnormalize
; NATIVE: ret

  %addr = getelementptr i8, ptr %base, i64 %index
  %v = load i64, ptr %addr
  ret i64 %v
}

define i64 @load_integer_address(i64 %base, i64 %index) {
; CHECK-LABEL: load_integer_address:
; CHECK: xnormalize64.ldx.reg a0, a1, a0
; CHECK-NEXT: ret
; OBJ-LABEL: <load_integer_address>:
; OBJ: xnormalize64.ldx.reg
; NATIVE-LABEL: load_integer_address:
; NATIVE-NOT: xnormalize
; NATIVE: ret

  %address = add i64 %base, %index
  %pointer = inttoptr i64 %address to ptr
  %value = load i64, ptr %pointer
  ret i64 %value
}

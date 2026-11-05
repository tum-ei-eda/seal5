; RUN: llc -O2 -mtriple=riscv32 -mattr=+xnormalize32 -verify-machineinstrs -global-isel=1 -global-isel-abort=1 < %s | FileCheck %s
; RUN: llc -O2 -mtriple=riscv32 -mattr=+xnormalize32 -verify-machineinstrs -global-isel=1 -global-isel-abort=1 -filetype=obj < %s -o %t.o
; RUN: llvm-objdump -d --mattr=+xnormalize32 %t.o | FileCheck %s --check-prefix=OBJ
; RUN: llc -O2 -mtriple=riscv32 -verify-machineinstrs -global-isel=1 -global-isel-abort=1 < %s | FileCheck %s --check-prefix=NATIVE

define i32 @ldx_reg(ptr %base, i32 %index) {
; CHECK-LABEL: ldx_reg:
; CHECK: xnormalize32.ldx.reg a0, a1, a0
; CHECK-NEXT: ret
; OBJ-LABEL: <ldx_reg>:
; OBJ: xnormalize32.ldx.reg
; NATIVE-LABEL: ldx_reg:
; NATIVE-NOT: xnormalize
; NATIVE: ret

  %addr = getelementptr i8, ptr %base, i32 %index
  %v = load i32, ptr %addr
  ret i32 %v
}

define i32 @load_integer_address(i32 %base, i32 %index) {
; CHECK-LABEL: load_integer_address:
; CHECK: xnormalize32.ldx.reg a0, a1, a0
; CHECK-NEXT: ret
; OBJ-LABEL: <load_integer_address>:
; OBJ: xnormalize32.ldx.reg
; NATIVE-LABEL: load_integer_address:
; NATIVE-NOT: xnormalize
; NATIVE: ret

  %address = add i32 %base, %index
  %pointer = inttoptr i32 %address to ptr
  %value = load i32, ptr %pointer
  ret i32 %value
}

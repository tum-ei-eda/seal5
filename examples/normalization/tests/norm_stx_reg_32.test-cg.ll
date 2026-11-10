; RUN: llc -O2 -mtriple=riscv32 -mattr=+xnormalize32 -verify-machineinstrs -global-isel=1 -global-isel-abort=1 < %s | FileCheck %s
; RUN: llc -O2 -mtriple=riscv32 -mattr=+xnormalize32 -verify-machineinstrs -global-isel=1 -global-isel-abort=1 -filetype=obj < %s -o %t.o
; RUN: llvm-objdump -d --mattr=+xnormalize32 %t.o | FileCheck %s --check-prefix=OBJ
; RUN: llc -O2 -mtriple=riscv32 -verify-machineinstrs -global-isel=1 -global-isel-abort=1 < %s | FileCheck %s --check-prefix=NATIVE

define void @stx_reg(ptr %base, i32 %index, i32 %data) {
; CHECK-LABEL: stx_reg:
; CHECK: xnormalize32.stx.reg a2, a1, a0
; CHECK-NEXT: ret
; OBJ-LABEL: <stx_reg>:
; OBJ: xnormalize32.stx.reg
; NATIVE-LABEL: stx_reg:
; NATIVE-NOT: xnormalize
; NATIVE: ret

  %addr = getelementptr i8, ptr %base, i32 %index
  store i32 %data, ptr %addr
  ret void
}

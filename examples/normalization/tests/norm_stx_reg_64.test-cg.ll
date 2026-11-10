; RUN: llc -O2 -mtriple=riscv64 -mattr=+xnormalize64 -verify-machineinstrs -global-isel=1 -global-isel-abort=1 < %s | FileCheck %s
; RUN: llc -O2 -mtriple=riscv64 -mattr=+xnormalize64 -verify-machineinstrs -global-isel=1 -global-isel-abort=1 -filetype=obj < %s -o %t.o
; RUN: llvm-objdump -d --mattr=+xnormalize64 %t.o | FileCheck %s --check-prefix=OBJ
; RUN: llc -O2 -mtriple=riscv64 -verify-machineinstrs -global-isel=1 -global-isel-abort=1 < %s | FileCheck %s --check-prefix=NATIVE

define void @stx_reg(ptr %base, i64 %index, i64 %data) {
; CHECK-LABEL: stx_reg:
; CHECK: xnormalize64.stx.reg a2, a1, a0
; CHECK-NEXT: ret
; OBJ-LABEL: <stx_reg>:
; OBJ: xnormalize64.stx.reg
; NATIVE-LABEL: stx_reg:
; NATIVE-NOT: xnormalize
; NATIVE: ret

  %addr = getelementptr i8, ptr %base, i64 %index
  store i64 %data, ptr %addr
  ret void
}

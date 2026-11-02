; RUN: llc -O2 -mtriple=riscv64 -mattr=+xnormalize64 -verify-machineinstrs -global-isel=1 -global-isel-abort=1 < %s | FileCheck %s
; RUN: llc -O2 -mtriple=riscv64 -mattr=+xnormalize64 -verify-machineinstrs -global-isel=1 -global-isel-abort=1 -filetype=obj < %s -o %t.o
; RUN: llvm-objdump -d --mattr=+xnormalize64 %t.o | FileCheck %s --check-prefix=OBJ
; RUN: llc -O2 -mtriple=riscv64 -verify-machineinstrs -global-isel=1 -global-isel-abort=1 < %s | FileCheck %s --check-prefix=NATIVE

define i64 @ldx_scale(ptr %base, i64 %index) {
; CHECK-LABEL: ldx_scale:
; CHECK: xnormalize64.ldx.scale a0, a0, a1
; CHECK-NEXT: ret
; OBJ-LABEL: <ldx_scale>:
; OBJ: xnormalize64.ldx.scale
; NATIVE-LABEL: ldx_scale:
; NATIVE-NOT: xnormalize
; NATIVE: ret

  %off = shl i64 %index, 2
  %addr = getelementptr i8, ptr %base, i64 %off
  %v = load i64, ptr %addr
  ret i64 %v
}

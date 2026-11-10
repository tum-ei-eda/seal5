; RUN: llc -O2 -mtriple=riscv32 -mattr=+xnormalize32 -verify-machineinstrs -global-isel=1 -global-isel-abort=1 < %s | FileCheck %s
; RUN: llc -O2 -mtriple=riscv32 -mattr=+xnormalize32 -verify-machineinstrs -global-isel=1 -global-isel-abort=1 -filetype=obj < %s -o %t.o
; RUN: llvm-objdump -d --mattr=+xnormalize32 %t.o | FileCheck %s --check-prefix=OBJ
; RUN: llc -O2 -mtriple=riscv32 -verify-machineinstrs -global-isel=1 -global-isel-abort=1 < %s | FileCheck %s --check-prefix=NATIVE

define void @stx_scale(ptr %base, i32 %index, i32 %data) {
; CHECK-LABEL: stx_scale:
; CHECK: xnormalize32.stx.scale a2, a0, a1
; CHECK-NEXT: ret
; OBJ-LABEL: <stx_scale>:
; OBJ: xnormalize32.stx.scale
; NATIVE-LABEL: stx_scale:
; NATIVE-NOT: xnormalize
; NATIVE: ret

  %off = shl i32 %index, 2
  %addr = getelementptr i8, ptr %base, i32 %off
  store i32 %data, ptr %addr
  ret void
}

; RUN: llc -O2 -mtriple=riscv32 -mattr=+xnormalize32 -verify-machineinstrs -global-isel=1 -global-isel-abort=1 < %s | FileCheck %s
; RUN: llc -O2 -mtriple=riscv32 -mattr=+xnormalize32 -verify-machineinstrs -global-isel=1 -global-isel-abort=1 -filetype=obj < %s -o %t.o
; RUN: llvm-objdump -d --mattr=+xnormalize32 %t.o | FileCheck %s --check-prefix=OBJ
; RUN: llc -O2 -mtriple=riscv32 -verify-machineinstrs -global-isel=1 -global-isel-abort=1 < %s | FileCheck %s --check-prefix=NATIVE

define i32 @ldx_scale(ptr %base, i32 %index) {
; CHECK-LABEL: ldx_scale:
; CHECK: xnormalize32.ldx.scale a0, a0, a1
; CHECK-NEXT: ret
; OBJ-LABEL: <ldx_scale>:
; OBJ: xnormalize32.ldx.scale
; NATIVE-LABEL: ldx_scale:
; NATIVE-NOT: xnormalize
; NATIVE: ret

  %off = shl i32 %index, 2
  %addr = getelementptr i8, ptr %base, i32 %off
  %v = load i32, ptr %addr
  ret i32 %v
}

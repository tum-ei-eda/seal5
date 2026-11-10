; RUN: llc -O2 -mtriple=riscv32 -mattr=+xnormalize32 -verify-machineinstrs -global-isel=1 -global-isel-abort=1 < %s | FileCheck %s
; RUN: llc -O2 -mtriple=riscv32 -mattr=+xnormalize32 -verify-machineinstrs -global-isel=1 -global-isel-abort=1 -filetype=obj < %s -o %t.o
; RUN: llvm-objdump -d --mattr=+xnormalize32 %t.o | FileCheck %s --check-prefix=OBJ
; RUN: llc -O2 -mtriple=riscv32 -verify-machineinstrs -global-isel=1 -global-isel-abort=1 < %s | FileCheck %s --check-prefix=NATIVE

define i32 @ld_both(ptr %base, i32 %index, i32 %bias) {
; CHECK-LABEL: ld_both:
; CHECK: xnormalize32.ld.both a0, a1, a0, a2
; CHECK-NEXT: ret
; OBJ-LABEL: <ld_both>:
; OBJ: xnormalize32.ld.both
; NATIVE-LABEL: ld_both:
; NATIVE-NOT: xnormalize
; NATIVE: ret

  %addr = getelementptr i8, ptr %base, i32 %index
  %v = load i32, ptr %addr
  %r = xor i32 %v, %bias
  ret i32 %r
}

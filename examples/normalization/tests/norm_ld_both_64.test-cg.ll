; RUN: llc -O2 -mtriple=riscv64 -mattr=+xnormalize64 -verify-machineinstrs -global-isel=1 -global-isel-abort=1 < %s | FileCheck %s
; RUN: llc -O2 -mtriple=riscv64 -mattr=+xnormalize64 -verify-machineinstrs -global-isel=1 -global-isel-abort=1 -filetype=obj < %s -o %t.o
; RUN: llvm-objdump -d --mattr=+xnormalize64 %t.o | FileCheck %s --check-prefix=OBJ
; RUN: llc -O2 -mtriple=riscv64 -verify-machineinstrs -global-isel=1 -global-isel-abort=1 < %s | FileCheck %s --check-prefix=NATIVE

define i64 @ld_both(ptr %base, i64 %index, i64 %bias) {
; CHECK-LABEL: ld_both:
; CHECK: xnormalize64.ld.both a0, a1, a0, a2
; CHECK-NEXT: ret
; OBJ-LABEL: <ld_both>:
; OBJ: xnormalize64.ld.both
; NATIVE-LABEL: ld_both:
; NATIVE-NOT: xnormalize
; NATIVE: ret

  %addr = getelementptr i8, ptr %base, i64 %index
  %v = load i64, ptr %addr
  %r = xor i64 %v, %bias
  ret i64 %r
}

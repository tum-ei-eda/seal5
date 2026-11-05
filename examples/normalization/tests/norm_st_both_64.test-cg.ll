; RUN: llc -O2 -mtriple=riscv64 -mattr=+xnormalize64 -verify-machineinstrs -global-isel=1 -global-isel-abort=1 < %s | FileCheck %s
; RUN: llc -O2 -mtriple=riscv64 -mattr=+xnormalize64 -verify-machineinstrs -global-isel=1 -global-isel-abort=1 -filetype=obj < %s -o %t.o
; RUN: llvm-objdump -d --mattr=+xnormalize64 %t.o | FileCheck %s --check-prefix=OBJ
; RUN: llc -O2 -mtriple=riscv64 -verify-machineinstrs -global-isel=1 -global-isel-abort=1 < %s | FileCheck %s --check-prefix=NATIVE

define void @st_both(ptr %base, i64 %index, i64 %a, i64 %b) {
; CHECK-LABEL: st_both:
; CHECK: xnormalize64.st.both a2, a0, a1, a3
; CHECK-NEXT: ret
; OBJ-LABEL: <st_both>:
; OBJ: xnormalize64.st.both
; NATIVE-LABEL: st_both:
; NATIVE-NOT: xnormalize
; NATIVE: ret

  %off = shl i64 %index, 2
  %addr = getelementptr i8, ptr %base, i64 %off
  %v = add i64 %a, %b
  store i64 %v, ptr %addr
  ret void
}

; RUN: llc -O2 -mtriple=riscv32 -mattr=+xnormalize32 -verify-machineinstrs -global-isel=1 -global-isel-abort=1 < %s | FileCheck %s
; RUN: llc -O2 -mtriple=riscv32 -mattr=+xnormalize32 -verify-machineinstrs -global-isel=1 -global-isel-abort=1 -filetype=obj < %s -o %t.o
; RUN: llvm-objdump -d --mattr=+xnormalize32 %t.o | FileCheck %s --check-prefix=OBJ
; RUN: llc -O2 -mtriple=riscv32 -verify-machineinstrs -global-isel=1 -global-isel-abort=1 < %s | FileCheck %s --check-prefix=NATIVE

define void @st_both(ptr %base, i32 %index, i32 %a, i32 %b) {
; CHECK-LABEL: st_both:
; CHECK: xnormalize32.st.both a2, a0, a1, a3
; CHECK-NEXT: ret
; OBJ-LABEL: <st_both>:
; OBJ: xnormalize32.st.both
; NATIVE-LABEL: st_both:
; NATIVE-NOT: xnormalize
; NATIVE: ret

  %off = shl i32 %index, 2
  %addr = getelementptr i8, ptr %base, i32 %off
  %v = add i32 %a, %b
  store i32 %v, ptr %addr
  ret void
}

; RUN: llc -O2 -mtriple=riscv64 -mattr=+xnormalize64 -verify-machineinstrs -global-isel=1 -global-isel-abort=1 < %s | FileCheck %s
; RUN: llc -O2 -mtriple=riscv64 -mattr=+xnormalize64 -verify-machineinstrs -global-isel=1 -global-isel-abort=1 -filetype=obj < %s -o %t.o
; RUN: llvm-objdump -d --mattr=+xnormalize64 %t.o | FileCheck %s --check-prefix=OBJ
; RUN: llc -O2 -mtriple=riscv64 -verify-machineinstrs -global-isel=1 -global-isel-abort=1 < %s | FileCheck %s --check-prefix=NATIVE

define void @st_xor(ptr %base, i64 %a, i64 %b) {
; CHECK-LABEL: st_xor:
; CHECK: xnormalize64.st.xor a1, a0, a2
; CHECK-NEXT: ret
; OBJ-LABEL: <st_xor>:
; OBJ: xnormalize64.st.xor
; NATIVE-LABEL: st_xor:
; NATIVE-NOT: xnormalize
; NATIVE: ret

  %v = xor i64 %a, %b
  store i64 %v, ptr %base
  ret void
}

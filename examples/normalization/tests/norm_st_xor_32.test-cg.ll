; RUN: llc -O2 -mtriple=riscv32 -mattr=+xnormalize32 -verify-machineinstrs -global-isel=1 -global-isel-abort=1 < %s | FileCheck %s
; RUN: llc -O2 -mtriple=riscv32 -mattr=+xnormalize32 -verify-machineinstrs -global-isel=1 -global-isel-abort=1 -filetype=obj < %s -o %t.o
; RUN: llvm-objdump -d --mattr=+xnormalize32 %t.o | FileCheck %s --check-prefix=OBJ
; RUN: llc -O2 -mtriple=riscv32 -verify-machineinstrs -global-isel=1 -global-isel-abort=1 < %s | FileCheck %s --check-prefix=NATIVE

define void @st_xor(ptr %base, i32 %a, i32 %b) {
; CHECK-LABEL: st_xor:
; CHECK: xnormalize32.st.xor a1, a0, a2
; CHECK-NEXT: ret
; OBJ-LABEL: <st_xor>:
; OBJ: xnormalize32.st.xor
; NATIVE-LABEL: st_xor:
; NATIVE-NOT: xnormalize
; NATIVE: ret

  %v = xor i32 %a, %b
  store i32 %v, ptr %base
  ret void
}

; RUN: llc -O2 -mtriple=riscv32 -mattr=+xnormalize32 -verify-machineinstrs -global-isel=1 -global-isel-abort=1 < %s | FileCheck %s
; RUN: llc -O2 -mtriple=riscv32 -mattr=+xnormalize32 -verify-machineinstrs -global-isel=1 -global-isel-abort=1 -filetype=obj < %s -o %t.o
; RUN: llvm-objdump -d --mattr=+xnormalize32 %t.o | FileCheck %s --check-prefix=OBJ
; RUN: llc -O2 -mtriple=riscv32 -verify-machineinstrs -global-isel=1 -global-isel-abort=1 < %s | FileCheck %s --check-prefix=NATIVE

define i32 @ld_add(ptr %base, i32 %bias) {
; CHECK-LABEL: ld_add:
; CHECK: xnormalize32.ld.add a0, a0, a1
; CHECK-NEXT: ret
; OBJ-LABEL: <ld_add>:
; OBJ: xnormalize32.ld.add
; NATIVE-LABEL: ld_add:
; NATIVE-NOT: xnormalize
; NATIVE: ret

  %v = load i32, ptr %base
  %r = add i32 %v, %bias
  ret i32 %r
}

define i32 @load_shared(ptr %base, i32 %bias) {
; OBJ-LABEL: <load_shared>:
; OBJ: xnormalize32.loadx
; CHECK-LABEL: load_shared:
; CHECK-NOT: xnormalize32.ld.add
; CHECK: xnormalize32.loadx
; CHECK-NEXT: add {{.*}}
; CHECK-NEXT: xor {{.*}}
; CHECK-NEXT: ret
; NATIVE-LABEL: load_shared:
; NATIVE-NOT: xnormalize
; NATIVE: ret

  %v = load volatile i32, ptr %base
  %sum = add i32 %v, %bias
  %r = xor i32 %sum, %v
  ret i32 %r
}

define i32 @load_before_store(ptr %base, i32 %bias, i32 %data) {
; OBJ-LABEL: <load_before_store>:
; OBJ: xnormalize32.loadx
; CHECK-LABEL: load_before_store:
; CHECK-NOT: xnormalize32.ld.add
; CHECK: xnormalize32.loadx
; CHECK-NOT: xnormalize32.ld.add
; CHECK-DAG: add {{.*}}
; CHECK-DAG: sw {{.*}}
; CHECK-NOT: xnormalize32.ld.add
; CHECK: ret
; NATIVE-LABEL: load_before_store:
; NATIVE-NOT: xnormalize
; NATIVE: ret

  %v = load i32, ptr %base
  store i32 %data, ptr %base
  %r = add i32 %v, %bias
  ret i32 %r
}

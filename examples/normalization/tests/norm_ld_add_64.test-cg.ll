; RUN: llc -O2 -mtriple=riscv64 -mattr=+xnormalize64 -verify-machineinstrs -global-isel=1 -global-isel-abort=1 < %s | FileCheck %s
; RUN: llc -O2 -mtriple=riscv64 -mattr=+xnormalize64 -verify-machineinstrs -global-isel=1 -global-isel-abort=1 -filetype=obj < %s -o %t.o
; RUN: llvm-objdump -d --mattr=+xnormalize64 %t.o | FileCheck %s --check-prefix=OBJ
; RUN: llc -O2 -mtriple=riscv64 -verify-machineinstrs -global-isel=1 -global-isel-abort=1 < %s | FileCheck %s --check-prefix=NATIVE

define i64 @ld_add(ptr %base, i64 %bias) {
; CHECK-LABEL: ld_add:
; CHECK: xnormalize64.ld.add a0, a0, a1
; CHECK-NEXT: ret
; OBJ-LABEL: <ld_add>:
; OBJ: xnormalize64.ld.add
; NATIVE-LABEL: ld_add:
; NATIVE-NOT: xnormalize
; NATIVE: ret

  %v = load i64, ptr %base
  %r = add i64 %v, %bias
  ret i64 %r
}

define i64 @load_shared(ptr %base, i64 %bias) {
; OBJ-LABEL: <load_shared>:
; OBJ: xnormalize64.load64
; CHECK-LABEL: load_shared:
; CHECK-NOT: xnormalize64.ld.add
; CHECK: xnormalize64.load64
; CHECK-NEXT: add {{.*}}
; CHECK-NEXT: xor {{.*}}
; CHECK-NEXT: ret
; NATIVE-LABEL: load_shared:
; NATIVE-NOT: xnormalize
; NATIVE: ret

  %v = load volatile i64, ptr %base
  %sum = add i64 %v, %bias
  %r = xor i64 %sum, %v
  ret i64 %r
}

define i64 @load_before_store(ptr %base, i64 %bias, i64 %data) {
; OBJ-LABEL: <load_before_store>:
; OBJ: xnormalize64.load64
; CHECK-LABEL: load_before_store:
; CHECK-NOT: xnormalize64.ld.add
; CHECK: xnormalize64.load64
; CHECK-NOT: xnormalize64.ld.add
; CHECK-DAG: add {{.*}}
; CHECK-DAG: sd {{.*}}
; CHECK-NOT: xnormalize64.ld.add
; CHECK: ret
; NATIVE-LABEL: load_before_store:
; NATIVE-NOT: xnormalize
; NATIVE: ret

  %v = load i64, ptr %base
  store i64 %data, ptr %base
  %r = add i64 %v, %bias
  ret i64 %r
}

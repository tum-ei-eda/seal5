; RUN: llc -O2 -mtriple=riscv64 -mattr=+xnormalize64 -verify-machineinstrs -global-isel=1 -global-isel-abort=1 < %s | FileCheck %s
; RUN: llc -O2 -mtriple=riscv64 -mattr=+xnormalize64 -verify-machineinstrs -global-isel=1 -global-isel-abort=1 -filetype=obj < %s -o %t.o
; RUN: llvm-objdump -d --mattr=+xnormalize64 %t.o | FileCheck %s --check-prefix=OBJ
; RUN: llc -O2 -mtriple=riscv64 -verify-machineinstrs -global-isel=1 -global-isel-abort=1 < %s | FileCheck %s --check-prefix=NATIVE

; Ordinary pointer/GEP and integer-address IR exercise address/data fusion.
; Shared volatile loads must execute once; aliasing stores prevent load motion.

define i64 @ldx_reg(ptr %base, i64 %index) {
; CHECK-LABEL: ldx_reg:
; CHECK: xnormalize64.ldx.reg a0, a1, a0
; CHECK-NEXT: ret
; OBJ-LABEL: <ldx_reg>:
; OBJ: xnormalize64.ldx.reg
; NATIVE-LABEL: ldx_reg:
; NATIVE-NOT: xnormalize
; NATIVE: ret

  %addr = getelementptr i8, ptr %base, i64 %index
  %v = load i64, ptr %addr
  ret i64 %v
}

define void @stx_reg(ptr %base, i64 %index, i64 %data) {
; CHECK-LABEL: stx_reg:
; CHECK: xnormalize64.stx.reg a2, a1, a0
; CHECK-NEXT: ret
; OBJ-LABEL: <stx_reg>:
; OBJ: xnormalize64.stx.reg
; NATIVE-LABEL: stx_reg:
; NATIVE-NOT: xnormalize
; NATIVE: ret

  %addr = getelementptr i8, ptr %base, i64 %index
  store i64 %data, ptr %addr
  ret void
}

define i64 @ldx_scale(ptr %base, i64 %index) {
; CHECK-LABEL: ldx_scale:
; CHECK: xnormalize64.ldx.scale a0, a0, a1
; CHECK-NEXT: ret
; OBJ-LABEL: <ldx_scale>:
; OBJ: xnormalize64.ldx.scale
; NATIVE-LABEL: ldx_scale:
; NATIVE-NOT: xnormalize
; NATIVE: ret

  %off = shl i64 %index, 2
  %addr = getelementptr i8, ptr %base, i64 %off
  %v = load i64, ptr %addr
  ret i64 %v
}

define void @stx_scale(ptr %base, i64 %index, i64 %data) {
; CHECK-LABEL: stx_scale:
; CHECK: xnormalize64.stx.scale a2, a0, a1
; CHECK-NEXT: ret
; OBJ-LABEL: <stx_scale>:
; OBJ: xnormalize64.stx.scale
; NATIVE-LABEL: stx_scale:
; NATIVE-NOT: xnormalize
; NATIVE: ret

  %off = shl i64 %index, 2
  %addr = getelementptr i8, ptr %base, i64 %off
  store i64 %data, ptr %addr
  ret void
}

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

define i64 @load_shared(ptr %base, i64 %bias) {
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

define i64 @load_integer_address(i64 %base, i64 %index) {
; CHECK-LABEL: load_integer_address:
; CHECK: xnormalize64.ldx.reg a0, a1, a0
; CHECK-NEXT: ret
; OBJ-LABEL: <load_integer_address>:
; OBJ: xnormalize64.ldx.reg
; NATIVE-LABEL: load_integer_address:
; NATIVE-NOT: xnormalize
; NATIVE: ret

  %address = add i64 %base, %index
  %pointer = inttoptr i64 %address to ptr
  %value = load i64, ptr %pointer
  ret i64 %value
}

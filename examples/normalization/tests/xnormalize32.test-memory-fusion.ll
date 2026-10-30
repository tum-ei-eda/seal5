; RUN: llc -O2 -mtriple=riscv32 -mattr=+xnormalize32 -verify-machineinstrs -global-isel=1 -global-isel-abort=1 < %s | FileCheck %s
; RUN: llc -O2 -mtriple=riscv32 -mattr=+xnormalize32 -verify-machineinstrs -global-isel=1 -global-isel-abort=1 -filetype=obj < %s -o %t.o
; RUN: llvm-objdump -d --mattr=+xnormalize32 %t.o | FileCheck %s --check-prefix=OBJ
; RUN: llc -O2 -mtriple=riscv32 -verify-machineinstrs -global-isel=1 -global-isel-abort=1 < %s | FileCheck %s --check-prefix=NATIVE

; Ordinary pointer/GEP and integer-address IR exercise address/data fusion.
; Shared volatile loads must execute once; aliasing stores prevent load motion.

define i32 @ldx_reg(ptr %base, i32 %index) {
; CHECK-LABEL: ldx_reg:
; CHECK: xnormalize32.ldx.reg a0, a1, a0
; CHECK-NEXT: ret
; OBJ-LABEL: <ldx_reg>:
; OBJ: xnormalize32.ldx.reg
; NATIVE-LABEL: ldx_reg:
; NATIVE-NOT: xnormalize
; NATIVE: ret

  %addr = getelementptr i8, ptr %base, i32 %index
  %v = load i32, ptr %addr
  ret i32 %v
}

define void @stx_reg(ptr %base, i32 %index, i32 %data) {
; CHECK-LABEL: stx_reg:
; CHECK: xnormalize32.stx.reg a2, a1, a0
; CHECK-NEXT: ret
; OBJ-LABEL: <stx_reg>:
; OBJ: xnormalize32.stx.reg
; NATIVE-LABEL: stx_reg:
; NATIVE-NOT: xnormalize
; NATIVE: ret

  %addr = getelementptr i8, ptr %base, i32 %index
  store i32 %data, ptr %addr
  ret void
}

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

define void @stx_scale(ptr %base, i32 %index, i32 %data) {
; CHECK-LABEL: stx_scale:
; CHECK: xnormalize32.stx.scale a2, a0, a1
; CHECK-NEXT: ret
; OBJ-LABEL: <stx_scale>:
; OBJ: xnormalize32.stx.scale
; NATIVE-LABEL: stx_scale:
; NATIVE-NOT: xnormalize
; NATIVE: ret

  %off = shl i32 %index, 2
  %addr = getelementptr i8, ptr %base, i32 %off
  store i32 %data, ptr %addr
  ret void
}

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

define i32 @load_shared(ptr %base, i32 %bias) {
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

define i32 @load_integer_address(i32 %base, i32 %index) {
; CHECK-LABEL: load_integer_address:
; CHECK: xnormalize32.ldx.reg a0, a1, a0
; CHECK-NEXT: ret
; OBJ-LABEL: <load_integer_address>:
; OBJ: xnormalize32.ldx.reg
; NATIVE-LABEL: load_integer_address:
; NATIVE-NOT: xnormalize
; NATIVE: ret

  %address = add i32 %base, %index
  %pointer = inttoptr i32 %address to ptr
  %value = load i32, ptr %pointer
  ret i32 %value
}

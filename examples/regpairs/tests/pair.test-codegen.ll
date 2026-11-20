; RUN: llc -mtriple=riscv32 -mattr=+m,+xregpairs -verify-machineinstrs %s -o - | FileCheck %s
; RUN: llc -O0 -mtriple=riscv32 -mattr=+m,+xregpairs -verify-machineinstrs %s -o %t.O0
; RUN: llc -O3 -mtriple=riscv32 -mattr=+m,+xregpairs -verify-machineinstrs %s -o %t.O3
; RUN: llc -mtriple=riscv32 -mattr=+m -verify-machineinstrs %s -o - | FileCheck %s --check-prefix=OFF
; RUN: llc -mtriple=riscv32 -mattr=+m,+xregpairs,-seal5-regpair32-add -verify-machineinstrs %s -o - | FileCheck %s --check-prefix=OFF
; OFF-NOT: pair.add
; OFF-NOT: padd.
; CHECK-LABEL: scalar_add:
; CHECK: pair.add64
; CHECK-NOT: padd.
define i64 @scalar_add(i64 %a, i64 %b) {
  %r = add i64 %a, %b
  ret i64 %r
}
; CHECK-LABEL: vector_add:
; CHECK: pair.add.2x32
; CHECK-NOT: padd.
define <2 x i32> @vector_add(<2 x i32> %a, <2 x i32> %b) {
  %r = add <2 x i32> %a, %b
  ret <2 x i32> %r
}
; CHECK-LABEL: unaligned_memory:
; CHECK: pair.add.2x32
; CHECK-NOT: padd.
define void @unaligned_memory(ptr %d, ptr %a, ptr %b) {
  %x = load <2 x i32>, ptr %a, align 1
  %y = load <2 x i32>, ptr %b, align 1
  %r = add <2 x i32> %x, %y
  store <2 x i32> %r, ptr %d, align 1
  ret void
}
; CHECK-LABEL: aligned_memory:
; CHECK: pair.add.2x32
; CHECK-NOT: padd.
define void @aligned_memory(ptr %d, ptr %a, ptr %b) {
  %x = load <2 x i32>, ptr %a, align 8
  %y = load <2 x i32>, ptr %b, align 4
  %r = add <2 x i32> %x, %y
  store <2 x i32> %r, ptr %d, align 8
  ret void
}
; CHECK-LABEL: extract_dynamic:
; CHECK-NOT: padd.
define i32 @extract_dynamic(<2 x i32> %a, i32 %i) {
  %r = extractelement <2 x i32> %a, i32 %i
  ret i32 %r
}
; CHECK-LABEL: fallback:
; CHECK-NOT: pair.
; CHECK-NOT: padd.
define <2 x i32> @fallback(<2 x i32> %a, <2 x i32> %b) {
  %r = xor <2 x i32> %a, %b
  ret <2 x i32> %r
}

; Additional arithmetic, construction and shuffle legality checks.
; CHECK-LABEL: sub:
define <2 x i32> @sub(<2 x i32> %a, <2 x i32> %b) {
 %r = sub <2 x i32> %a, %b
 ret <2 x i32> %r
}
define <2 x i32> @mul(<2 x i32> %a, <2 x i32> %b) {
 %r = mul <2 x i32> %a, %b
 ret <2 x i32> %r
}
define <2 x i32> @and(<2 x i32> %a, <2 x i32> %b) {
 %r = and <2 x i32> %a, %b
 ret <2 x i32> %r
}
define <2 x i32> @or(<2 x i32> %a, <2 x i32> %b) {
 %r = or <2 x i32> %a, %b
 ret <2 x i32> %r
}
define <2 x i32> @xor(<2 x i32> %a, <2 x i32> %b) {
 %r = xor <2 x i32> %a, %b
 ret <2 x i32> %r
}
define <2 x i32> @shl(<2 x i32> %a, <2 x i32> %b) {
 %r = shl <2 x i32> %a, %b
 ret <2 x i32> %r
}
define <2 x i32> @lshr(<2 x i32> %a, <2 x i32> %b) {
 %r = lshr <2 x i32> %a, %b
 ret <2 x i32> %r
}
define <2 x i32> @ashr(<2 x i32> %a, <2 x i32> %b) {
 %r = ashr <2 x i32> %a, %b
 ret <2 x i32> %r
}
define <2 x i32> @udiv(<2 x i32> %a, <2 x i32> %b) {
 %r = udiv <2 x i32> %a, %b
 ret <2 x i32> %r
}
define <2 x i32> @sdiv(<2 x i32> %a, <2 x i32> %b) {
 %r = sdiv <2 x i32> %a, %b
 ret <2 x i32> %r
}
define <2 x i32> @insert(<2 x i32> %a, i32 %x, i32 %i) {
 %r = insertelement <2 x i32> %a, i32 %x, i32 %i
 ret <2 x i32> %r
}
define <2 x i32> @shuffle(<2 x i32> %a, <2 x i32> %b) {
 %r = shufflevector <2 x i32> %a, <2 x i32> %b, <2 x i32> <i32 3, i32 0>
 ret <2 x i32> %r
}
define <2 x i32> @constant() { ret <2 x i32> <i32 123, i32 456> }

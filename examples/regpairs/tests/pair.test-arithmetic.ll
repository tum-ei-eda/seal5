; RUN: llc -mtriple=riscv32 -mattr=+m,+xregpairs -verify-machineinstrs %s -o - | FileCheck %s
; RUN: llc -mtriple=riscv32 -mattr=+xregpairs -verify-machineinstrs %s -o - | FileCheck %s
; RUN: llc -O0 -mtriple=riscv32 -mattr=+m,+xregpairs -verify-machineinstrs %s -o %t.O0
; RUN: llc -O3 -mtriple=riscv32 -mattr=+m,+xregpairs -verify-machineinstrs %s -o %t.O3
; RUN: llc -mtriple=riscv32 -mattr=+m -verify-machineinstrs %s -o - | FileCheck %s --check-prefix=OFF
; Disabling a required capability also clears the parent ISA feature in LLVM.
; RUN: llc -mtriple=riscv32 -mattr=+m,+xregpairs,-seal5-regpair32-sub -verify-machineinstrs %s -o - | FileCheck %s --check-prefix=OFF
; RUN: llc -mtriple=riscv32 -mattr=+m,+xregpairs,-seal5-regpair32-mul -verify-machineinstrs %s -o - | FileCheck %s --check-prefix=OFF
; RUN: llc -mtriple=riscv32 -mattr=+m,+seal5-regpair32,+seal5-regpair32-sub,+seal5-regpair32-mul -verify-machineinstrs %s -o - | FileCheck %s --check-prefix=OFF
; OFF-NOT: {{^[ \t]+pair\.}}
; OFF-NOT: padd.
; CHECK-LABEL: scalar_sub:
; CHECK: pair.sub64
; CHECK-NOT: padd.
define i64 @scalar_sub(i64 %a, i64 %b) {
  %r = sub i64 %a, %b
  ret i64 %r
}
; CHECK-LABEL: vector_sub:
; CHECK: pair.sub.2x32
; CHECK-NOT: padd.
define <2 x i32> @vector_sub(<2 x i32> %a, <2 x i32> %b) {
  %r = sub <2 x i32> %a, %b
  ret <2 x i32> %r
}
; CHECK-LABEL: vector_mul:
; CHECK: pair.mul.2x32
; CHECK-NOT: padd.
define <2 x i32> @vector_mul(<2 x i32> %a, <2 x i32> %b) {
  %r = mul <2 x i32> %a, %b
  ret <2 x i32> %r
}

; A full scalar product includes cross-word terms; packed MUL is not equivalent.
; CHECK-LABEL: scalar_mul_fallback:
; CHECK-NOT: pair.mul.2x32
define i64 @scalar_mul_fallback(i64 %a, i64 %b) {
  %r = mul i64 %a, %b
  ret i64 %r
}

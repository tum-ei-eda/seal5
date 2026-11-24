; RUN: llc -mtriple=riscv32 -mattr=+m,+xregpairs -riscv-seal5-regpair-bitops=false -verify-machineinstrs %s -o - | FileCheck %s --check-prefix=LIMIT
; RUN: llc -mtriple=riscv32 -mattr=+m,+xregpairs -verify-machineinstrs %s -o - | FileCheck %s
; RUN: llc -O0 -mtriple=riscv32 -mattr=+m,+xregpairs -verify-machineinstrs %s -o %t.O0
; RUN: llc -O3 -mtriple=riscv32 -mattr=+m,+xregpairs -verify-machineinstrs %s -o %t.O3
; RUN: llc -mtriple=riscv32 -mattr=+m,+xregpairs,-seal5-regpair32-logic,-seal5-regpair32-shift -verify-machineinstrs %s -o - | FileCheck %s --check-prefix=OFF
; OFF-NOT: pair.xor64
; OFF-NOT: pair.and64
; OFF-NOT: pair.slli64
; OFF-NOT: pair.srli64
; OFF-NOT: pair.srai64
; OFF-NOT: pair.rori64
; CHECK-LABEL: native_xor64:
; CHECK: pair.xor64
define i64 @native_xor64(i64 %a,i64 %b) {
 %r=xor i64 %a,%b
 ret i64 %r
}
; CHECK-LABEL: native_and64:
; CHECK: pair.and64
define i64 @native_and64(i64 %a,i64 %b) {
 %r=and i64 %a,%b
 ret i64 %r
}
; CHECK-LABEL: native_slli64_1:
; CHECK: pair.slli64
define i64 @native_slli64_1(i64 %a) {
 %r=shl i64 %a,1
 ret i64 %r
}
; CHECK-LABEL: native_slli64_31:
; CHECK: pair.slli64
define i64 @native_slli64_31(i64 %a) {
 %r=shl i64 %a,31
 ret i64 %r
}
; CHECK-LABEL: native_slli64_32:
; CHECK-NOT: pair.slli64
; CHECK: ret
define i64 @native_slli64_32(i64 %a) {
 %r=shl i64 %a,32
 ret i64 %r
}
; CHECK-LABEL: native_slli64_33:
; CHECK-NOT: pair.slli64
; CHECK: ret
define i64 @native_slli64_33(i64 %a) {
 %r=shl i64 %a,33
 ret i64 %r
}
; CHECK-LABEL: native_slli64_63:
; CHECK-NOT: pair.slli64
; CHECK: ret
define i64 @native_slli64_63(i64 %a) {
 %r=shl i64 %a,63
 ret i64 %r
}
define i64 @variable_slli64(i64 %a,i64 %n) {
 %r=shl i64 %a,%n
 ret i64 %r
}
; CHECK-LABEL: native_srli64_1:
; CHECK: pair.srli64
define i64 @native_srli64_1(i64 %a) {
 %r=lshr i64 %a,1
 ret i64 %r
}
; CHECK-LABEL: native_srli64_31:
; CHECK: pair.srli64
define i64 @native_srli64_31(i64 %a) {
 %r=lshr i64 %a,31
 ret i64 %r
}
; CHECK-LABEL: native_srli64_32:
; CHECK-NOT: pair.srli64
; CHECK: ret
define i64 @native_srli64_32(i64 %a) {
 %r=lshr i64 %a,32
 ret i64 %r
}
; CHECK-LABEL: native_srli64_33:
; CHECK-NOT: pair.srli64
; CHECK: ret
define i64 @native_srli64_33(i64 %a) {
 %r=lshr i64 %a,33
 ret i64 %r
}
; CHECK-LABEL: native_srli64_63:
; CHECK-NOT: pair.srli64
; CHECK: ret
define i64 @native_srli64_63(i64 %a) {
 %r=lshr i64 %a,63
 ret i64 %r
}
define i64 @variable_srli64(i64 %a,i64 %n) {
 %r=lshr i64 %a,%n
 ret i64 %r
}
; CHECK-LABEL: native_srai64_1:
; CHECK: pair.srai64
define i64 @native_srai64_1(i64 %a) {
 %r=ashr i64 %a,1
 ret i64 %r
}
; CHECK-LABEL: native_srai64_31:
; CHECK: pair.srai64
define i64 @native_srai64_31(i64 %a) {
 %r=ashr i64 %a,31
 ret i64 %r
}
; CHECK-LABEL: native_srai64_32:
; CHECK-NOT: pair.srai64
; CHECK: ret
define i64 @native_srai64_32(i64 %a) {
 %r=ashr i64 %a,32
 ret i64 %r
}
; CHECK-LABEL: native_srai64_33:
; CHECK-NOT: pair.srai64
; CHECK: ret
define i64 @native_srai64_33(i64 %a) {
 %r=ashr i64 %a,33
 ret i64 %r
}
; CHECK-LABEL: native_srai64_63:
; CHECK-NOT: pair.srai64
; CHECK: ret
define i64 @native_srai64_63(i64 %a) {
 %r=ashr i64 %a,63
 ret i64 %r
}
define i64 @variable_srai64(i64 %a,i64 %n) {
 %r=ashr i64 %a,%n
 ret i64 %r
}
declare i64 @llvm.fshr.i64(i64,i64,i64)
declare i64 @llvm.fshl.i64(i64,i64,i64)
; CHECK-LABEL: rotate_right:
; CHECK: pair.rori64
define i64 @rotate_right(i64 %a) {
 %r=call i64 @llvm.fshr.i64(i64 %a,i64 %a,i64 19)
 ret i64 %r
}
; CHECK-LABEL: rotate_left:
; CHECK: pair.rori64
define i64 @rotate_left(i64 %a) {
 %r=call i64 @llvm.fshl.i64(i64 %a,i64 %a,i64 19)
 ret i64 %r
}
define i64 @rotate_variable(i64 %a,i64 %n) {
 %r=call i64 @llvm.fshr.i64(i64 %a,i64 %a,i64 %n)
 ret i64 %r
}

; LIMIT-NOT: pair.xor64
; LIMIT-NOT: pair.and64
; LIMIT-NOT: pair.slli64
; LIMIT-NOT: pair.srli64
; LIMIT-NOT: pair.srai64
; LIMIT-NOT: pair.rori64
; LIMIT: pair.add64
; CHECK-LABEL: keep_add64:
; CHECK: pair.add64
define i64 @keep_add64(i64 %a, i64 %b) {
 %r=add i64 %a,%b
 ret i64 %r
}

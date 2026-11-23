; RUN: llc -mtriple=riscv32 -mattr=+xregpairs -verify-machineinstrs -O0 %s -o - | FileCheck %s
; RUN: llc -mtriple=riscv32 -mattr=+xregpairs -verify-machineinstrs -O2 %s -o - | FileCheck %s
; RUN: llc -mtriple=riscv32 -mattr=+xregpairs -verify-machineinstrs -O3 %s -o - | FileCheck %s

declare i64 @llvm.riscv.xregpairs.add64(i64, i64)
declare i64 @llvm.riscv.xregpairs.add.2x32(i64, i64)

define i64 @add64(i64 %a, i64 %b) {
; CHECK-LABEL: add64:
; CHECK: pair.add64
  %r = call i64 @llvm.riscv.xregpairs.add64(i64 %a, i64 %b)
  ret i64 %r
}
define i64 @add_2x32(i64 %a, i64 %b) {
; CHECK-LABEL: add_2x32:
; CHECK: pair.add.2x32
  %r = call i64 @llvm.riscv.xregpairs.add.2x32(i64 %a, i64 %b)
  ret i64 %r
}
; An i64 argument following an i32 argument occupies an odd/even ABI pair.
; The instruction must be allocated an even/odd physical pair and copy as needed.
define i64 @unaligned_abi(i32 %prefix, i64 %a, i64 %b) {
; CHECK-LABEL: unaligned_abi:
; CHECK: pair.add64
  %r = call i64 @llvm.riscv.xregpairs.add64(i64 %a, i64 %b)
  %p = zext i32 %prefix to i64
  %s = call i64 @llvm.riscv.xregpairs.add64(i64 %r, i64 %p)
  ret i64 %s
}

declare i64 @llvm.riscv.xregpairs.sub64(i64, i64)
define i64 @sub64(i64 %a, i64 %b) {
; CHECK-LABEL: sub64:
; CHECK: pair.sub64
  %r = call i64 @llvm.riscv.xregpairs.sub64(i64 %a, i64 %b)
  ret i64 %r
}

declare i64 @llvm.riscv.xregpairs.sub.2x32(i64, i64)
define i64 @sub_2x32(i64 %a, i64 %b) {
; CHECK-LABEL: sub_2x32:
; CHECK: pair.sub.2x32
  %r = call i64 @llvm.riscv.xregpairs.sub.2x32(i64 %a, i64 %b)
  ret i64 %r
}

declare i64 @llvm.riscv.xregpairs.mul.2x32(i64, i64)
define i64 @mul_2x32(i64 %a, i64 %b) {
; CHECK-LABEL: mul_2x32:
; CHECK: pair.mul.2x32
  %r = call i64 @llvm.riscv.xregpairs.mul.2x32(i64 %a, i64 %b)
  ret i64 %r
}

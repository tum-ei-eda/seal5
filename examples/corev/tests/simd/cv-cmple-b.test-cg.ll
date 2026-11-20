; Swapping the operands and predicate selects an equivalent CORE-V encoding.
; RUN: llc -mtriple=riscv32 -mattr=+m,+xcorevsimd -verify-machineinstrs %s -o - | FileCheck %s
; RUN: llc -mtriple=riscv32 -mattr=+m,+xcorevsimd -global-isel=1 -global-isel-abort=1 -verify-machineinstrs %s -o - | FileCheck %s

define i32 @packed_cmple_b(i32 %a, i32 %b) {
; CHECK-LABEL: packed_cmple_b:
; CHECK: {{seal5\.cv\.cmple\.b[ \t]+a0, a0, a1|seal5\.cv\.cmpge\.b[ \t]+a0, a1, a0}}
  %av = bitcast i32 %a to <4 x i8>
  %bv = bitcast i32 %b to <4 x i8>
  %c = icmp sle <4 x i8> %av, %bv
  %r = sext <4 x i1> %c to <4 x i8>
  %ret = bitcast <4 x i8> %r to i32
  ret i32 %ret
}

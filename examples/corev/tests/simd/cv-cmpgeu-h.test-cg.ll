; Swapping the operands and predicate selects an equivalent CORE-V encoding.
; RUN: llc -mtriple=riscv32 -mattr=+m,+xcorevsimd -verify-machineinstrs %s -o - | FileCheck %s
; RUN: llc -mtriple=riscv32 -mattr=+m,+xcorevsimd -global-isel=1 -global-isel-abort=1 -verify-machineinstrs %s -o - | FileCheck %s

define i32 @packed_cmpgeu_h(i32 %a, i32 %b) {
; CHECK-LABEL: packed_cmpgeu_h:
; CHECK: {{seal5\.cv\.cmpgeu\.h[ \t]+a0, a0, a1|seal5\.cv\.cmpleu\.h[ \t]+a0, a1, a0}}
  %av = bitcast i32 %a to <2 x i16>
  %bv = bitcast i32 %b to <2 x i16>
  %c = icmp uge <2 x i16> %av, %bv
  %r = sext <2 x i1> %c to <2 x i16>
  %ret = bitcast <2 x i16> %r to i32
  ret i32 %ret
}

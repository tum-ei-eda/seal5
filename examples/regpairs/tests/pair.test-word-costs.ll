; RUN: llc -mtriple=riscv32 -mattr=+m,+xregpairs -verify-machineinstrs %s -o - | FileCheck %s
; A masked multiply must remain one MUL + one MULHU, without a call or
; a pair operation that obscures the zero upper words.
; CHECK-LABEL: multiply_low_words:
; CHECK-NOT: pair.
; CHECK-NOT: call
; CHECK-DAG: mulhu
; CHECK-DAG: {{[ \t]mul[ \t]}}
; CHECK-NOT: {{[ \t]mul[ \t]}}
; CHECK-NOT: mulhu
; CHECK-NOT: pair.
; CHECK-NOT: call
; CHECK: ret
define i64 @multiply_low_words(i64 %a, i64 %b) {
 %al = and i64 %a, 4294967295
 %bl = and i64 %b, 4294967295
 %p = mul nuw i64 %al, %bl
 ret i64 %p
}
; CHECK-LABEL: multiply_high_words:
; CHECK-NOT: pair.
; CHECK-NOT: call
; CHECK-DAG: mulhu
; CHECK-DAG: {{[ \t]mul[ \t]}}
; CHECK-NOT: {{[ \t]mul[ \t]}}
; CHECK-NOT: mulhu
; CHECK-NOT: pair.
; CHECK-NOT: call
; CHECK: ret
define i64 @multiply_high_words(i64 %a, i64 %b) {
 %ah = lshr i64 %a, 32
 %bh = lshr i64 %b, 32
 %p = mul nuw i64 %ah, %bh
 ret i64 %p
}
; CHECK-LABEL: mask_high_word:
; CHECK-NOT: pair.and64
; CHECK: ret
define i64 @mask_high_word(i64 %a) {
 %r = and i64 %a, -4294967296
 ret i64 %r
}
; A genuine two-word mask can still select the pair instruction.
; CHECK-LABEL: mask_two_words:
; CHECK: pair.and64
define i64 @mask_two_words(i64 %a) {
 %r = and i64 %a, 71777214294589695
 ret i64 %r
}

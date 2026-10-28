; RUN: llc -O3 -mtriple=riscv64 -mattr=+xnormalize64 -verify-machineinstrs -global-isel=1 < %s | FileCheck %s

define i64 @wordnand(i64 %a, i64 %b) {
; CHECK-LABEL: wordnand:
; CHECK: xnormalize64.wordnand a0, {{(a0, a1|a1, a0)}}
  %a32 = trunc i64 %a to i32
  %b32 = trunc i64 %b to i32
  %both = and i32 %a32, %b32
  %inv = xor i32 %both, -1
  %result = sext i32 %inv to i64
  ret i64 %result
}

define i64 @wordnor(i64 %a, i64 %b) {
; CHECK-LABEL: wordnor:
; CHECK: xnormalize64.wordnor a0, {{(a0, a1|a1, a0)}}
  %a32 = trunc i64 %a to i32
  %b32 = trunc i64 %b to i32
  %either = or i32 %a32, %b32
  %inv = xor i32 %either, -1
  %result = sext i32 %inv to i64
  ret i64 %result
}

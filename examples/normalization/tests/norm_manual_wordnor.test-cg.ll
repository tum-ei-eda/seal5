; RUN: llc -O2 -mtriple=riscv64 -mattr=+xnormalize64 -verify-machineinstrs -global-isel=1 -global-isel-abort=1 < %s | FileCheck %s
; RUN: llc -O2 -mtriple=riscv64 -mattr=+xnormalize64 -verify-machineinstrs -global-isel=1 -global-isel-abort=1 -filetype=obj < %s -o %t.o
; RUN: llvm-objdump -d --mattr=+xnormalize64 %t.o | FileCheck %s --check-prefix=OBJ

define i64 @wordnor(i64 %a, i64 %b) {
; OBJ-LABEL: <wordnor>:
; OBJ: xnormalize64.wordnor
; CHECK-LABEL: wordnor:
; CHECK: xnormalize64.wordnor a0, {{(a0, a1|a1, a0)}}
  %a32 = trunc i64 %a to i32
  %b32 = trunc i64 %b to i32
  %either = or i32 %a32, %b32
  %inv = xor i32 %either, -1
  %result = sext i32 %inv to i64
  ret i64 %result
}

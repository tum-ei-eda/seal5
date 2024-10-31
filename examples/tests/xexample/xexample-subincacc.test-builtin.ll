; RUN: llc -O3 -mtriple=riscv32 -mattr=+xexample -verify-machineinstrs < %s \
; RUN:   | FileCheck %s

declare i32 @llvm.riscv.subincacc(i32, i32, i32)

define i32 @subincacc(i32 %a, i32 %b, i32 %c) {
; CHECK-LABEL: subincacc:
; CHECK:       # %bb.0:
; CHECK-NEXT:    xexample.subincacc a0, a1, a2
; CHECK-NEXT:    ret
  %1 = call i32 @llvm.riscv.subincacc(i32 %a, i32 %b, i32 %c)
  ret i32 %1
}

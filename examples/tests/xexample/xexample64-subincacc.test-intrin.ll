; RUN: llc -O3 -mtriple=riscv64 -mattr=+xexample -verify-machineinstrs < %s \
; RUN:   | FileCheck %s

declare i64 @llvm.riscv.subincacc(i64, i64, i64)

define i64 @subincacc(i64 %a, i64 %b, i64 %c) {
; CHECK-LABEL: subincacc:
; CHECK:       # %bb.0:
; CHECK-NEXT:    xexample64.subincacc a0, a1, a2
; CHECK-NEXT:    ret
  %1 = call i64 @llvm.riscv.subincacc(i64 %a, i64 %b, i64 %c)
  ret i64 %1
}

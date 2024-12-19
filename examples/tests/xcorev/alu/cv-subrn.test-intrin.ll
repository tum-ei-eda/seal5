; RUN: llc -O3 -mtriple=riscv32 -mattr=+xcorevalu -verify-machineinstrs < %s \
; RUN:   | FileCheck %s

declare i32 @llvm.riscv.xcorevalu.alu.subrn(i32, i32, i32)

define i32 @test_subrn(i32 %a, i32 %b) {
; CHECK-LABEL: test_subrn:
; CHECK:       # %bb.0:
; CHECK-NEXT:    seal5.cv.subrn a0, a1, 15
; CHECK-NEXT:    ret
  %1 = call i32 @llvm.riscv.xcorevalu.alu.subrn(i32 %a, i32 %b, i32 15)
  ret i32 %1
}

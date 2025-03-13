; RUN: llc -O3 -mtriple=riscv32 -mattr=+xcorevalu -verify-machineinstrs < %s \
; RUN:   | FileCheck %s

declare i32 @llvm.riscv.xcorevalu.alu.sletu(i32, i32)

define i32 @test_sletu(i32 %a, i32 %b) {
; CHECK-LABEL: test_sletu:
; CHECK:       # %bb.0:
; CHECK-NEXT:    seal5.cv.sletu a0, a0, a1
; CHECK-NEXT:    ret
  %1 = call i32 @llvm.riscv.xcorevalu.alu.sletu(i32 %a, i32 %b)
  ret i32 %1
}

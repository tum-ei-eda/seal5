; RUN: llc -O3 -mtriple=riscv32 -mattr=+xcorevalu -verify-machineinstrs < %s \
; RUN:   | FileCheck %s

declare i32 @llvm.riscv.xcorevalu.alu.clipu(i32, i32)

define i32 @test_clipu(i32 %a) {
; CHECK-LABEL: test_clipu:
; CHECK:       # %bb.0:
; CHECK-NEXT:    seal5.cv.clipu a0, a0, 15
; CHECK-NEXT:    ret
  %1 = call i32 @llvm.riscv.xcorevalu.alu.clipu(i32 %a, i32 15)
  ret i32 %1
}

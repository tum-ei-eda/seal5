; RUN: llc -O3 -mtriple=riscv32 -mattr=+xcorevalu -verify-machineinstrs < %s \
; RUN:   | FileCheck %s

declare i32 @llvm.riscv.xcorevalu.alu.clip(i32, i32)

define i32 @test_clip(i32 %a) {
; CHECK-LABEL: test_clip:
; CHECK:       # %bb.0:
; CHECK-NEXT:    seal5.cv.clip a0, a0, 15
; CHECK-NEXT:    ret
  %1 = call i32 @llvm.riscv.xcorevalu.alu.clip(i32 %a, i32 15)
  ret i32 %1
}

; RUN: llc -O3 -mtriple=riscv32 -mattr=+xcorevalu -verify-machineinstrs < %s \
; RUN:   | FileCheck %s

declare i32 @llvm.riscv.xcorevalu.alu.extbs(i32)

define i32 @test_extbs(i32 %a) {
; CHECK-LABEL: test_extbs:
; CHECK:       # %bb.0:
; CHECK-NEXT:    seal5.cv.extbs a0, a0
; CHECK-NEXT:    ret
  %1 = call i32 @llvm.riscv.xcorevalu.alu.extbs(i32 %a)
  ret i32 %1
}

; RUN: llc -O3 -mtriple=riscv32 -mattr=+xcorevalu -verify-machineinstrs < %s \
; RUN:   | FileCheck %s

declare i32 @llvm.riscv.xcorevalu.alu.addrnr(i32, i32, i32)

define i32 @test_addrnr(i32 %a, i32 %b, i32 %c) {
; CHECK-LABEL: test_addrnr:
; CHECK:       # %bb.0:
; CHECK-NEXT:    seal5.cv.addrnr a0, a1, a2
; CHECK-NEXT:    ret
  %1 = call i32 @llvm.riscv.xcorevalu.alu.addrnr(i32 %a, i32 %b, i32 %c)
  ret i32 %1
}

define i32 @test_addrnr2(i32 %a, i32 %b) {
; CHECK-LABEL: test_addrnr2:
; CHECK:       # %bb.0:
; CHECK-NEXT:    seal5.cv.addrnr a0, a1, a2
; CHECK-NEXT:    ret
  %1 = call i32 @llvm.riscv.xcorevalu.alu.addrnr(i32 %a, i32 %b, i32 15)
  ret i32 %1
}

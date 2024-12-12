; RUN: llc -O3 -mtriple=riscv32 -mattr=+xcorevalu -verify-machineinstrs < %s \
; RUN:   | FileCheck %s

declare i32 @llvm.riscv.xcorevalu.alu.clip(i32, i32)

define i32 @test_clipr(i32 %a, i32 %b) {
; CHECK-LABEL: test_clipr:
; CHECK:       # %bb.0:
; CHECK-NEXT:    seal5.cv.clipr a0, a0, a1
; CHECK-NEXT:    ret
  %1 = call i32 @llvm.riscv.xcorevalu.alu.clip(i32 %a, i32 %b)
  ret i32 %1
}

define i32 @test_clipr2(i32 %a, i32 %b) {
; CHECK-LABEL: test_clipr2:
; CHECK:       # %bb.0:
; CHECK-NEXT:    seal5.cv.clipr a0, a0, a1
; CHECK-NEXT:    ret
  %1 = call i32 @llvm.riscv.xcorevalu.alu.clip(i32 %a, i32 32)
  ret i32 %1
}

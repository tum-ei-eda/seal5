; RUN: llc -O3 -mtriple=riscv32 -mattr=+xcorevalu -verify-machineinstrs < %s \
; RUN:   | FileCheck %s

declare i32 @llvm.riscv.xcorevalu.alu.exthz(i32)

define i32 @test_exthz(i32 %a) {
; CHECK-LABEL: test_exthz:
; CHECK:       # %bb.0:
; CHECK-NEXT:    seal5.cv.exthz a0, a0
; CHECK-NEXT:    ret
  %1 = call i32 @llvm.riscv.xcorevalu.alu.exthz(i32 %a)
  ret i32 %1
}

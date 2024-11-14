; RUN: llc -O3 -mtriple=riscv32 -mattr=+xcorevnand -verify-machineinstrs < %s \
; RUN:   | FileCheck %s

declare i32 @llvm.riscv.xcv.nand.bitwise(i32, i32)

define i32 @nand(i32 %a, i32 %b) {
; CHECK-LABEL: nand:
; CHECK:       # %bb.0:
; CHECK-NEXT:    cv.nand.bitwise a0, a1
; CHECK-NEXT:    ret
  %1 = call i32 @llvm.riscv.xcv.nand.bitwise(i32 %a, i32 %b)
  ret i32 %1
}

; RUN: llc -O0 -mtriple=riscv32 -mattr=+m,+xcorevbi -verify-machineinstrs -global-isel=1 -global-isel-abort=1 %s -o - | FileCheck %s
; RUN: llc -O3 -mtriple=riscv32 -mattr=+m,+xcorevbi -verify-machineinstrs -global-isel=1 -global-isel-abort=1 %s -o - | FileCheck %s

define i32 @bneimm(i32 %a) {
; CHECK-LABEL: bneimm:
; CHECK: seal5.cv.bneimm {{[a-z0-9]+}}, 5,
; CHECK: ret
; CHECK: ret
  %condition = icmp ne i32 %a, 5
  br i1 %condition, label %taken, label %other
other:
  ret i32 0
taken:
  ret i32 1
}

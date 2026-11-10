; RUN: llc -O0 -mtriple=riscv32 -mattr=+m,+xcorevbitmanip -verify-machineinstrs -global-isel=0 < %s | FileCheck %s
; RUN: llc -O3 -mtriple=riscv32 -mattr=+m,+xcorevbitmanip -verify-machineinstrs -global-isel=0 < %s | FileCheck %s
; RUN: llc -O0 -mtriple=riscv32 -mattr=+m,+xcorevbitmanip -verify-machineinstrs -global-isel=1 -global-isel-abort=1 < %s | FileCheck %s
; RUN: llc -O3 -mtriple=riscv32 -mattr=+m,+xcorevbitmanip -verify-machineinstrs -global-isel=1 -global-isel-abort=1 < %s | FileCheck %s
; RUN: llc -O3 -mtriple=riscv32 -mattr=+m,+xcorevbitmanip,-seal5-rotate32 -verify-machineinstrs -global-isel=0 < %s | FileCheck %s --check-prefix=BASE --implicit-check-not=seal5.cv.ror
; RUN: llc -O3 -mtriple=riscv32 -mattr=+m,+xcorevbitmanip,-seal5-rotate32 -verify-machineinstrs -global-isel=1 -global-isel-abort=1 < %s | FileCheck %s --check-prefix=BASE --implicit-check-not=seal5.cv.ror
; RUN: llc -O0 -mtriple=riscv64 -mattr=+m,+seal5-rotate32 -verify-machineinstrs -global-isel=0 < %s | FileCheck %s --check-prefix=BASE --implicit-check-not=seal5.cv.ror
; RUN: llc -O0 -mtriple=riscv64 -mattr=+m,+seal5-rotate32 -verify-machineinstrs -global-isel=1 -global-isel-abort=1 < %s | FileCheck %s --check-prefix=BASE --implicit-check-not=seal5.cv.ror

declare i32 @llvm.fshr.i32(i32, i32, i32)

define i32 @test_ror(i32 %a, i32 %b) {
; CHECK-LABEL: test_ror:
; BASE-LABEL: test_ror:
; CHECK-NOT: sll
; CHECK-NOT: srl
; CHECK: seal5.cv.ror
; CHECK-NOT: sll
; CHECK-NOT: srl
; CHECK: ret
  %result = call i32 @llvm.fshr.i32(i32 %a, i32 %a, i32 %b)
  ret i32 %result
}

define i32 @test_ror_masked(i32 %a, i32 %b) {
; CHECK-LABEL: test_ror_masked:
; BASE-LABEL: test_ror_masked:
; CHECK-NOT: sll
; CHECK-NOT: srl
; CHECK: seal5.cv.ror
; CHECK-NOT: sll
; CHECK-NOT: srl
; CHECK: ret
  %masked = and i32 %b, 31
  %result = call i32 @llvm.fshr.i32(i32 %a, i32 %a, i32 %masked)
  ret i32 %result
}

define i32 @test_ror_one(i32 %a) {
; CHECK-LABEL: test_ror_one:
; BASE-LABEL: test_ror_one:
; CHECK-NOT: sll
; CHECK-NOT: srl
; CHECK: seal5.cv.ror
; CHECK-NOT: sll
; CHECK-NOT: srl
; CHECK: ret
  %result = call i32 @llvm.fshr.i32(i32 %a, i32 %a, i32 1)
  ret i32 %result
}

define i32 @test_ror_33(i32 %a) {
; CHECK-LABEL: test_ror_33:
; BASE-LABEL: test_ror_33:
; CHECK-NOT: sll
; CHECK-NOT: srl
; CHECK: seal5.cv.ror
; CHECK-NOT: sll
; CHECK-NOT: srl
; CHECK: ret
  %result = call i32 @llvm.fshr.i32(i32 %a, i32 %a, i32 33)
  ret i32 %result
}

define i32 @test_ror_zero(i32 %a) {
; CHECK-LABEL: test_ror_zero:
; BASE-LABEL: test_ror_zero:
; CHECK-NOT: sll
; CHECK-NOT: srl
; CHECK: ret
  %result = call i32 @llvm.fshr.i32(i32 %a, i32 %a, i32 0)
  ret i32 %result
}

define i32 @test_ror_32(i32 %a) {
; CHECK-LABEL: test_ror_32:
; BASE-LABEL: test_ror_32:
; CHECK-NOT: sll
; CHECK-NOT: srl
; CHECK: ret
  %result = call i32 @llvm.fshr.i32(i32 %a, i32 %a, i32 32)
  ret i32 %result
}

define i32 @test_funnel(i32 %a, i32 %b, i32 %amount) {
; CHECK-LABEL: test_funnel:
; BASE-LABEL: test_funnel:
; CHECK-NOT: seal5.cv.ror
; CHECK: ret
  %result = call i32 @llvm.fshr.i32(i32 %a, i32 %b, i32 %amount)
  ret i32 %result
}

; RUN: llc -O2 -mtriple=riscv64 -mattr=+xnormalize64 -verify-machineinstrs -global-isel=1 -global-isel-abort=1 < %s | FileCheck %s
; RUN: llc -O2 -mtriple=riscv64 -mattr=+xnormalize64 -verify-machineinstrs -global-isel=1 -global-isel-abort=1 -filetype=obj < %s -o %t.o
; RUN: llvm-objdump -d --mattr=+xnormalize64 %t.o | FileCheck %s --check-prefix=OBJ

; XOR-nonzero is equivalent to register inequality (its optimized IR form).

define void @band(i64 %a, i64 %b) {
; CHECK-LABEL: band:
; CHECK-NOT: and a
; CHECK: xnormalize64.band
; OBJ-LABEL: <band>:
; OBJ: xnormalize64.band

  %v = and i64 %a, %b
  %c = icmp ne i64 %v, 0
  br i1 %c, label %taken, label %fall
fall:
  call void asm sideeffect "addi zero, zero, 1", ""()
  ret void
taken:
  call void asm sideeffect "nop", ""()
  ret void
}

define void @bor(i64 %a, i64 %b) {
; CHECK-LABEL: bor:
; CHECK-NOT: or a
; CHECK: xnormalize64.bor
; OBJ-LABEL: <bor>:
; OBJ: xnormalize64.bor

  %v = or i64 %a, %b
  %c = icmp ne i64 %v, 0
  br i1 %c, label %taken, label %fall
fall:
  call void asm sideeffect "addi zero, zero, 1", ""()
  ret void
taken:
  call void asm sideeffect "nop", ""()
  ret void
}

define void @bxor(i64 %a, i64 %b) {
; CHECK-LABEL: bxor:
; CHECK: xnormalize64.bxor
; OBJ-LABEL: <bxor>:
; OBJ: xnormalize64.bxor

  %c = icmp ne i64 %a, %b
  br i1 %c, label %taken, label %fall
fall:
  call void asm sideeffect "addi zero, zero, 1", ""()
  ret void
taken:
  call void asm sideeffect "nop", ""()
  ret void
}

define void @bnz(i64 %a) {
; CHECK-LABEL: bnz:
; CHECK: xnormalize64.bnz
; OBJ-LABEL: <bnz>:
; OBJ: xnormalize64.bnz

  %c = icmp ne i64 %a, 0
  br i1 %c, label %taken, label %fall
fall:
  call void asm sideeffect "addi zero, zero, 1", ""()
  ret void
taken:
  call void asm sideeffect "nop", ""()
  ret void
}

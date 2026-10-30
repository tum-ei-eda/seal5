; RUN: llc -O2 -mtriple=riscv32 -mattr=+xnormalize32 -verify-machineinstrs -global-isel=1 -global-isel-abort=1 < %s | FileCheck %s
; RUN: llc -O2 -mtriple=riscv32 -mattr=+xnormalize32 -verify-machineinstrs -global-isel=1 -global-isel-abort=1 -filetype=obj < %s -o %t.o
; RUN: llvm-objdump -d --mattr=+xnormalize32 %t.o | FileCheck %s --check-prefix=OBJ

; XOR-nonzero is equivalent to register inequality (its optimized IR form).

define void @band(i32 %a, i32 %b) {
; CHECK-LABEL: band:
; CHECK-NOT: and a
; CHECK: xnormalize32.band
; OBJ-LABEL: <band>:
; OBJ: xnormalize32.band

  %v = and i32 %a, %b
  %c = icmp ne i32 %v, 0
  br i1 %c, label %taken, label %fall
fall:
  call void asm sideeffect "addi zero, zero, 1", ""()
  ret void
taken:
  call void asm sideeffect "nop", ""()
  ret void
}

define void @bor(i32 %a, i32 %b) {
; CHECK-LABEL: bor:
; CHECK-NOT: or a
; CHECK: xnormalize32.bor
; OBJ-LABEL: <bor>:
; OBJ: xnormalize32.bor

  %v = or i32 %a, %b
  %c = icmp ne i32 %v, 0
  br i1 %c, label %taken, label %fall
fall:
  call void asm sideeffect "addi zero, zero, 1", ""()
  ret void
taken:
  call void asm sideeffect "nop", ""()
  ret void
}

define void @bxor(i32 %a, i32 %b) {
; CHECK-LABEL: bxor:
; CHECK: xnormalize32.bxor
; OBJ-LABEL: <bxor>:
; OBJ: xnormalize32.bxor

  %c = icmp ne i32 %a, %b
  br i1 %c, label %taken, label %fall
fall:
  call void asm sideeffect "addi zero, zero, 1", ""()
  ret void
taken:
  call void asm sideeffect "nop", ""()
  ret void
}

define void @bnz(i32 %a) {
; CHECK-LABEL: bnz:
; CHECK: xnormalize32.bnz
; OBJ-LABEL: <bnz>:
; OBJ: xnormalize32.bnz

  %c = icmp ne i32 %a, 0
  br i1 %c, label %taken, label %fall
fall:
  call void asm sideeffect "addi zero, zero, 1", ""()
  ret void
taken:
  call void asm sideeffect "nop", ""()
  ret void
}

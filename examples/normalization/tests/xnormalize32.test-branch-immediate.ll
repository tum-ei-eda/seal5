; RUN: llc -O2 -mtriple=riscv32 -mattr=+xnormalize32 -verify-machineinstrs -global-isel=1 -global-isel-abort=1 < %s | FileCheck %s
; RUN: llc -O2 -mtriple=riscv32 -mattr=+xnormalize32 -verify-machineinstrs -global-isel=1 -global-isel-abort=1 -filetype=obj < %s -o %t.o
; RUN: llvm-objdump -d --mattr=+xnormalize32 %t.o | FileCheck %s --check-prefix=OBJ

define void @signed5_min(i32 %value) {
; CHECK-LABEL: signed5_min:
; CHECK: xnormalize32.beqi5 a0, -16,
; OBJ-LABEL: <signed5_min>:
; OBJ: xnormalize32.beqi5
  %condition = icmp eq i32 %value, -16
  br i1 %condition, label %taken, label %fall
fall:
  call void asm sideeffect "addi zero, zero, 1", ""()
  ret void
taken:
  call void asm sideeffect "nop", ""()
  ret void
}

define void @signed5_max(i32 %value) {
; CHECK-LABEL: signed5_max:
; CHECK: xnormalize32.beqi5 a0, 15,
  %condition = icmp eq i32 %value, 15
  br i1 %condition, label %taken, label %fall
fall:
  call void asm sideeffect "addi zero, zero, 1", ""()
  ret void
taken:
  call void asm sideeffect "nop", ""()
  ret void
}

define void @signed5_too_large(i32 %value) {
; CHECK-LABEL: signed5_too_large:
; CHECK-NOT: xnormalize32.beqi5
; CHECK: ret
  %condition = icmp eq i32 %value, 16
  br i1 %condition, label %taken, label %fall
fall:
  call void asm sideeffect "addi zero, zero, 1", ""()
  ret void
taken:
  call void asm sideeffect "nop", ""()
  ret void
}

define void @unsigned3_max(i32 %value) {
; CHECK-LABEL: unsigned3_max:
; CHECK: xnormalize32.bltui3 a0, 7,
  %condition = icmp ult i32 %value, 7
  br i1 %condition, label %taken, label %fall
fall:
  call void asm sideeffect "addi zero, zero, 1", ""()
  ret void
taken:
  call void asm sideeffect "nop", ""()
  ret void
}

define void @signed8_min(i32 %value) {
; CHECK-LABEL: signed8_min:
; CHECK: xnormalize32.bnei8 a0, -128,
  %condition = icmp ne i32 %value, -128
  br i1 %condition, label %taken, label %fall
fall:
  call void asm sideeffect "addi zero, zero, 1", ""()
  ret void
taken:
  call void asm sideeffect "nop", ""()
  ret void
}

define void @signed8_max(i32 %value) {
; CHECK-LABEL: signed8_max:
; CHECK: xnormalize32.bnei8 a0, 127,
  %condition = icmp ne i32 %value, 127
  br i1 %condition, label %taken, label %fall
fall:
  call void asm sideeffect "addi zero, zero, 1", ""()
  ret void
taken:
  call void asm sideeffect "nop", ""()
  ret void
}

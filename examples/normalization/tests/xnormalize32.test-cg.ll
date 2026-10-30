; RUN: llc -O3 -mtriple=riscv32 -mattr=+xnormalize32 -verify-machineinstrs -global-isel=1 < %s | FileCheck %s
; RUN: llc -O3 -mtriple=riscv32 -mattr=+xnormalize32 -verify-machineinstrs -global-isel=1 -filetype=obj < %s -o %t.o
; RUN: llvm-objdump -d --mattr=+xnormalize32 %t.o | FileCheck %s --check-prefix=OBJ

define i32 @load16(ptr %p) {
; CHECK-LABEL: load16:
; CHECK: xnormalize32.load16 a0, a0
  %v = load i16, ptr %p, align 2
  %r = zext i16 %v to i32
  ret i32 %r
}

define i32 @loadx(ptr %p) {
; CHECK-LABEL: loadx:
; CHECK: xnormalize32.loadx a0, a0
  %v = load i32, ptr %p, align 4
  ret i32 %v
}

define i32 @load8(ptr %p) {
; CHECK-LABEL: load8:
; CHECK: xnormalize32.load8 a0, a0
  %v = load i8, ptr %p, align 1
  %r = zext i8 %v to i32
  ret i32 %r
}

define void @store16(ptr %p, i32 %v) {
; CHECK-LABEL: store16:
; CHECK: xnormalize32.store16 a1, a0
  %short = trunc i32 %v to i16
  store i16 %short, ptr %p, align 2
  ret void
}

define void @branch_equal(i32 %a, i32 %b) {
; CHECK-LABEL: branch_equal:
; CHECK: xnormalize32.branch
; OBJ-LABEL: <branch_equal>:
; OBJ: xnormalize32.branch
  %eq = icmp eq i32 %a, %b
  br i1 %eq, label %yes, label %no
no:
  call void asm sideeffect "addi zero, zero, 1", ""()
  ret void
yes:
  call void asm sideeffect "nop", ""()
  ret void
}

define i32 @extract8(i32 %value) {
; CHECK-LABEL: extract8:
; CHECK: xnormalize32.extract a0, a0, 8
  %shift = lshr i32 %value, 8
  %result = and i32 %shift, 255
  ret i32 %result
}

define i32 @extract4(i32 %value) {
; CHECK-LABEL: extract4:
; CHECK: xnormalize32.extract4 a0, a0, 8
  %shift = lshr i32 %value, 8
  %result = and i32 %shift, 15
  ret i32 %result
}

define i32 @extract8_unaligned(i32 %value) {
; CHECK-LABEL: extract8_unaligned:
; CHECK: xnormalize32.extract a0, a0, 3
  %shift = lshr i32 %value, 3
  %result = and i32 %shift, 255
  ret i32 %result
}

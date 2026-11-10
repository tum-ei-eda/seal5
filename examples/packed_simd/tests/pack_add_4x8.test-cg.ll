; RUN: llc -mtriple=riscv32 -O2 -mattr=+xpackedsimd32,+gpr32v -global-isel=1 -global-isel-abort=1 -verify-machineinstrs %s -o - | FileCheck %s
; RUN: llc -mtriple=riscv32 -O2 -mattr=+xpackedsimd32,+gpr32v -global-isel=0 -verify-machineinstrs %s -o - | FileCheck %s
; RUN: llc -mtriple=riscv32 -O2 -mattr=+xpackedsimd32,+gpr32v -global-isel=1 -global-isel-abort=1 -filetype=obj %s -o %t.o
; RUN: llvm-objdump -d --mattr=+xpackedsimd32 %t.o | FileCheck %s --check-prefix=OBJ
; RUN: llc -mtriple=riscv32 -O2 -mattr=+xpackedsimd32,-gpr32v -global-isel=0 %s -o - | FileCheck %s --check-prefix=NATIVE

; CHECK-LABEL: packed_add_4x8:
; CHECK: pack.add.4x8
; OBJ-LABEL: <packed_add_4x8>:
; OBJ: pack.add.4x8
; NATIVE-LABEL: packed_add_4x8:
; NATIVE-NOT: pack.
; NATIVE: ret

define i32 @packed_add_4x8(i32 %a, i32 %b) {
  %av = bitcast i32 %a to <4 x i8>
  %bv = bitcast i32 %b to <4 x i8>
  %result = add <4 x i8> %av, %bv
  %packed = bitcast <4 x i8> %result to i32
  ret i32 %packed
}

; CHECK-LABEL: packed_induction:
; CHECK: pack.add.4x8
; OBJ-LABEL: <packed_induction>:
; OBJ: pack.add.4x8
; NATIVE-LABEL: packed_induction:
; NATIVE-NOT: pack.
; NATIVE: ret

define void @packed_induction(ptr %out, i32 %n) {
entry:
  %run = icmp sgt i32 %n, 0
  br i1 %run, label %loop, label %exit
loop:
  %i = phi i32 [ 0, %entry ], [ %next, %loop ]
  %v = phi <4 x i8> [ <i8 0, i8 1, i8 2, i8 3>, %entry ], [ %inc, %loop ]
  %addr = getelementptr <4 x i8>, ptr %out, i32 %i
  store <4 x i8> %v, ptr %addr, align 1
  %inc = add <4 x i8> %v, <i8 4, i8 4, i8 4, i8 4>
  %next = add i32 %i, 1
  %done = icmp eq i32 %next, %n
  br i1 %done, label %exit, label %loop
exit:
  ret void
}

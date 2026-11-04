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

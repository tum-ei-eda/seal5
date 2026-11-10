; RUN: llc -mtriple=riscv32 -O2 -mattr=+xpackedsimd32,+gpr32v -global-isel=1 -global-isel-abort=1 -verify-machineinstrs %s -o - | FileCheck %s
; RUN: llc -mtriple=riscv32 -O2 -mattr=+xpackedsimd32,+gpr32v -global-isel=0 -verify-machineinstrs %s -o - | FileCheck %s
; RUN: llc -mtriple=riscv32 -O2 -mattr=+xpackedsimd32,+gpr32v -global-isel=1 -global-isel-abort=1 -filetype=obj %s -o %t.o
; RUN: llvm-objdump -d --mattr=+xpackedsimd32 %t.o | FileCheck %s --check-prefix=OBJ
; RUN: llc -mtriple=riscv32 -O2 -mattr=+xpackedsimd32,-gpr32v -global-isel=0 %s -o - | FileCheck %s --check-prefix=NATIVE

; CHECK-LABEL: packed_sub_2x16:
; CHECK: pack.sub.2x16 a0, a0, a1
; OBJ-LABEL: <packed_sub_2x16>:
; OBJ: pack.sub.2x16
; NATIVE-LABEL: packed_sub_2x16:
; NATIVE-NOT: pack.
; NATIVE: ret

define i32 @packed_sub_2x16(i32 %a, i32 %b) {
  %av = bitcast i32 %a to <2 x i16>
  %bv = bitcast i32 %b to <2 x i16>
  %result = sub <2 x i16> %av, %bv
  %packed = bitcast <2 x i16> %result to i32
  ret i32 %packed
}

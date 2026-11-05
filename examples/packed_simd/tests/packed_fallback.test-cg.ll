; RUN: llc -mtriple=riscv32 -O2 -mattr=+m,+xpackedsimd32,+gpr32v -global-isel=0 -verify-machineinstrs %s -o - | FileCheck %s
; RUN: llc -mtriple=riscv32 -O2 -mattr=+m,+xpackedsimd32,+gpr32v -global-isel=1 -global-isel-abort=1 -verify-machineinstrs %s -o - | FileCheck %s
; RUN: llc -mtriple=riscv32 -O2 -mattr=+m,+gpr32v,-xpackedsimd32,-gpr32v-add,-gpr32v-sub -global-isel=0 -verify-machineinstrs %s -o - | FileCheck %s --check-prefix=NOISA
; RUN: llc -mtriple=riscv32 -O2 -mattr=+m,+gpr32v,-xpackedsimd32,-gpr32v-add,-gpr32v-sub -global-isel=1 -global-isel-abort=1 -verify-machineinstrs %s -o - | FileCheck %s --check-prefix=NOISA

; CHECK-LABEL: dsp:
; CHECK: mul
; CHECK: pack.add.2x16
; CHECK: ret
; NOISA-LABEL: dsp:
; NOISA-NOT: pack.
; NOISA: ret
define void @dsp(ptr %a, ptr %b, ptr %out) {
  %x = load <2 x i16>, ptr %a, align 2
  %y = load <2 x i16>, ptr %b, align 2
  %wide = sext <2 x i16> %x to <2 x i32>
  %prod = mul <2 x i32> %wide, <i32 12345, i32 12345>
  %shifted = ashr <2 x i32> %prod, <i32 15, i32 15>
  %narrow = trunc <2 x i32> %shifted to <2 x i16>
  %sum = add <2 x i16> %y, %narrow
  store <2 x i16> %sum, ptr %out, align 2
  ret void
}

; CHECK-LABEL: narrow:
; CHECK: ret
; NOISA-LABEL: narrow:
; NOISA-NOT: pack.
; NOISA: ret
define void @narrow(ptr %p, ptr %out) {
  %v = load <2 x i8>, ptr %p, align 1
  %wide = zext <2 x i8> %v to <2 x i16>
  %mask = icmp ugt <2 x i16> %wide, <i16 127, i16 3>
  %selected = select <2 x i1> %mask, <2 x i16> %wide, <2 x i16> <i16 7, i16 9>
  %bytes = trunc <2 x i16> %selected to <2 x i8>
  store <2 x i8> %bytes, ptr %out, align 1
  ret void
}

; CHECK-LABEL: shuffle:
; CHECK: ret
; NOISA-LABEL: shuffle:
; NOISA-NOT: pack.
; NOISA: ret
define i32 @shuffle(i32 %a) {
  %v = bitcast i32 %a to <4 x i8>
  %s = shufflevector <4 x i8> %v, <4 x i8> poison, <4 x i32> <i32 3, i32 0, i32 2, i32 1>
  %x = extractelement <4 x i8> %s, i32 0
  %i = insertelement <4 x i8> %s, i8 %x, i32 1
  %word = bitcast <4 x i8> %i to i32
  ret i32 %word
}

; RUN: llc -O0 -mtriple=riscv32 -mattr=+m,+xcorevmac -verify-machineinstrs -global-isel=0 < %s | FileCheck %s
; RUN: llc -O3 -mtriple=riscv32 -mattr=+m,+xcorevmac -verify-machineinstrs -global-isel=0 < %s | FileCheck %s
; RUN: llc -O0 -mtriple=riscv32 -mattr=+m,+xcorevmac -verify-machineinstrs -global-isel=1 -global-isel-abort=1 < %s | FileCheck %s
; RUN: llc -O3 -mtriple=riscv32 -mattr=+m,+xcorevmac -verify-machineinstrs -global-isel=1 -global-isel-abort=1 < %s | FileCheck %s
; RUN: llc -O3 -mtriple=riscv32 -mattr=+m,+xcorevmac -global-isel=1 -global-isel-abort=1 -stop-before=instruction-select < %s | FileCheck %s --check-prefix=MASK
; RUN: llc -O3 -mtriple=riscv32 -mattr=+m -global-isel=1 -global-isel-abort=1 -stop-before=instruction-select < %s | FileCheck %s --check-prefix=BASE


define i32 @mulu(i32 %a, i32 %b) {
; CHECK-LABEL: mulu:
; MASK-LABEL: name: mulu
; MASK-NOT: G_CONSTANT_FOLD_BARRIER
; MASK: G_MUL
; BASE-LABEL: name: mulu
; BASE: G_CONSTANT_FOLD_BARRIER
; CHECK: seal5.cv.mulun {{[^,]+}}, {{[^,]+}}, {{[^,]+}}, 0
; CHECK: ret
  %1 = and i32 %a, 65535
  %2 = and i32 %b, 65535
  %3 = mul i32 %1, %2
  ret i32 %3
}

; Masks used by an add are not folded by the multiply instructions.
define i32 @masked_add(i32 %a, i32 %b) {
; CHECK-LABEL: masked_add:
; CHECK-NOT: seal5.cv.mulun
; CHECK: ret
; MASK-LABEL: name: masked_add
; MASK: G_CONSTANT_FOLD_BARRIER
  %lo_a = and i32 %a, 65535
  %lo_b = and i32 %b, 65535
  %sum = add i32 %lo_a, %lo_b
  ret i32 %sum
}

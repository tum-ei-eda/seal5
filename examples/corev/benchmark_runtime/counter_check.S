// SPDX-License-Identifier: Apache-2.0
.text
.global main
main:
  addi sp, sp, -16
  sw ra, 12(sp)
.global seal5_measure_start
seal5_measure_start:
  li t0, 10
1:
  // cv.add.h zero, zero, zero: verify custom-instruction counting as well.
  .word 0x0000007b
  addi t0, t0, -1
  bnez t0, 1b
.global seal5_measure_end
seal5_measure_end:
  la a0, success
  call puts
  li a0, 0
  lw ra, 12(sp)
  addi sp, sp, 16
  ret
.section .rodata
success:
  .string "SEAL5_RESULT verified=1"

# SPDX-License-Identifier: Apache-2.0
.section .text.start,"ax"
.globl _start
_start:
.option push
.option norelax
  la gp, __global_pointer$
.option pop
  li sp, 0x87fff000
  la t0, __bss_start
  la t1, __bss_end
1:
  bgeu t0, t1, 2f
  sw zero, 0(t0)
  addi t0, t0, 4
  j 1b
2:
  call seal5_main
  slli a0, a0, 1
  ori a0, a0, 1
  la t0, tohost
  sw a0, 0(t0)
3:
  wfi
  j 3b
.section .tohost,"aw",@progbits
.balign 64
.globl tohost
 tohost: .dword 0
.balign 64
.globl fromhost
 fromhost: .dword 0

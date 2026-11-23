# SPDX-License-Identifier: Apache-2.0
.text
.globl pair_alias_test
pair_alias_test:
  mv t0, ra
  li a0, -1
  li a1, 1
  li a2, 1
  li a3, 2
  pair.add64 a0, a0, a2
  bnez a0, 1f
  li t1, 4
  bne a1, t1, 1f
  pair.add64 zero, a0, a2
  bne ra, t0, 1f
  pair.add64 a0, zero, zero
  or a0, a0, a1
  bnez a0, 1f
  bne ra, t0, 1f
  li a0, -1
  li a1, -1
  pair.add.2x32 a0, a0, a0
  li t1, -2
  bne a0, t1, 1f
  bne a1, t1, 1f
  # Scalar borrow, with destination overlapping the second source.
  li a0, 0
  li a1, 1
  li a2, 1
  li a3, 0
  pair.sub64 a2, a0, a2
  li t1, -1
  bne a2, t1, 1f
  bnez a3, 1f
  # Packed subtraction must not borrow between lanes.
  li a0, 0
  li a1, 5
  li a2, 1
  li a3, 3
  pair.sub.2x32 a0, a0, a2
  bne a0, t1, 1f
  li t1, 2
  bne a1, t1, 1f
  # Both products wrap independently, with destination == second source.
  li a0, -1
  li a1, 0x80000000
  li a2, 2
  li a3, 3
  pair.mul.2x32 a2, a0, a2
  li t1, -2
  bne a2, t1, 1f
  li t1, 0x80000000
  bne a3, t1, 1f
  # Zero pair is 64-bit zero and must not read the return address.
  pair.sub64 a0, zero, a2
  li t1, 2
  bne a0, t1, 1f
  li t1, 0x7fffffff
  bne a1, t1, 1f
  pair.sub64 zero, a0, a2
  pair.sub.2x32 zero, a0, a2
  pair.mul.2x32 zero, a0, a2
  bne ra, t0, 1f
  pair.sub.2x32 a0, zero, zero
  or a0, a0, a1
  bnez a0, 1f
  pair.mul.2x32 a0, zero, a2
  or a0, a0, a1
  bnez a0, 1f
  bne ra, t0, 1f
  li a0, 0
  ret
1:
  li a0, 1
  ret

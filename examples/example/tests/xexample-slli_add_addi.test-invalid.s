#
# Generated on Tue, 08 Jul 2025 09:42:51 +0200.
#
# This file contains the Info for generating invalid tests for the XExample
# core architecture.



# RUN: not llvm-mc -triple=riscv32 --mattr=+xexample %s 2>&1\# RUN:        | FileCheck %s --check-prefixes=CHECK-ERROR

xexample.slli_add_addi 0, a2, a7, 15, 3
# CHECK-ERROR: invalid operands for instruction

xexample.slli_add_addi a0, 0, a7, 15, 3
# CHECK-ERROR: invalid operands for instruction

xexample.slli_add_addi a0, a2, 0, 15, 3
# CHECK-ERROR: invalid operands for instruction

xexample.slli_add_addi a0, a2, a7, a3, 3
# CHECK-ERROR: invalid operands for instruction

xexample.slli_add_addi a0, a2, a7, 15
# CHECK-ERROR: too few operands for instruction

xexample.slli_add_addi a2, a7, 15, a4
# CHECK-ERROR: too few operands for instruction

xexample.slli_add_addi a0, a2, a7, 15, 3, zero
# CHECK-ERROR: too many operands for instruction

xexample.slli_add_addi a0, a2, a7, 15, -1
# CHECK-ERROR: immediate must be an integer in the range [0, 31]

xexample.slli_add_addi a0, a2, a7, 15, 32
# CHECK-ERROR: immediate must be an integer in the range [0, 31]


xexample.slli_add_addi a0, a2, a7, 15, a5
# CHECK-ERROR: immediate must be an integer



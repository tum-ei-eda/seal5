#
# Generated on Fri, 04 Jul 2025 07:56:07 +0200.
#
# This file contains the Info for generating invalid tests for the XExample
# core architecture.



# RUN: not llvm-mc -triple=riscv32 --mattr=+xexample %s 2>&1\# RUN:        | FileCheck %s --check-prefixes=CHECK-ERROR

xexample.slli_add_addi 0, a5, a7, 27, 2
# CHECK-ERROR: invalid operands for instruction

xexample.slli_add_addi a1, 0, a7, 27, 2
# CHECK-ERROR: invalid operands for instruction

xexample.slli_add_addi a1, a5, 0, 27, 2
# CHECK-ERROR: invalid operands for instruction

xexample.slli_add_addi a1, a5, a7, a3, 2
# CHECK-ERROR: invalid operands for instruction

xexample.slli_add_addi a1, a5, a7, 27
# CHECK-ERROR: too few operands for instruction

xexample.slli_add_addi a5, a7, 27, a4
# CHECK-ERROR: too few operands for instruction

xexample.slli_add_addi a1, a5, a7, 27, 2, zero
# CHECK-ERROR: too many operands for instruction

xexample.slli_add_addi a1, a5, a7, 27, -1
# CHECK-ERROR: immediate must be an integer in the range [0, 31]

xexample.slli_add_addi a1, a5, a7, 27, 32
# CHECK-ERROR: immediate must be an integer in the range [0, 31]


xexample.slli_add_addi a1, a5, a7, 27, a5
# CHECK-ERROR: immediate must be an integer



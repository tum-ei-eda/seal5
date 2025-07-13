#
# Generated on Mon, 14 Jul 2025 01:09:17 +0200.
#
# This file contains the Info for generating invalid tests for the XExample
# core architecture.


# RUN: not llvm-mc -triple=riscv32 --mattr=+xexample %s 2>&1 \
# RUN:        | FileCheck %s --check-prefixes=CHECK-ERROR

xexample.slli_add_addi 0, a4, a6, 11, 0 # CHECK-ERROR: invalid operands for instruction
xexample.slli_add_addi a1, 0, a6, 11, 0 # CHECK-ERROR: invalid operands for instruction
xexample.slli_add_addi a1, a4, 0, 11, 0 # CHECK-ERROR: invalid operands for instruction
xexample.slli_add_addi a1, a4, a6, a3, 0 # CHECK-ERROR: invalid operands for instruction
xexample.slli_add_addi a1, a4, a6, 11 # CHECK-ERROR: too few operands for instruction

xexample.slli_add_addi a4, a6, 11, a4 # CHECK-ERROR: too few operands for instruction
xexample.slli_add_addi a1, a4, a6, 11, 0, zero # CHECK-ERROR: too many operands for instruction
xexample.slli_add_addi a1, a4, a6, 11, -1 # CHECK-ERROR: immediate must be an integer in the range [0, 31]
xexample.slli_add_addi a1, a4, a6, 11, 32 # CHECK-ERROR: immediate must be an integer in the range [0, 31]
xexample.slli_add_addi a1, a4, a6, 11, a5 # CHECK-ERROR: immediate must be an integer

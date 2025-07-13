#
# Generated on Mon, 14 Jul 2025 01:09:17 +0200.
#
# This file contains the Info for generating invalid tests for the XExample
# core architecture.


# RUN: not llvm-mc -triple=riscv32 --mattr=+xexample %s 2>&1 \
# RUN:        | FileCheck %s --check-prefixes=CHECK-ERROR

xexample.subincacc 0, a2, a5 # CHECK-ERROR: invalid operands for instruction
xexample.subincacc a0, 0, a5 # CHECK-ERROR: invalid operands for instruction
xexample.subincacc a0, a2, 0 # CHECK-ERROR: invalid operands for instruction
xexample.subincacc a0, a2 # CHECK-ERROR: too few operands for instruction
xexample.subincacc a2, a5 # CHECK-ERROR: too few operands for instruction
xexample.subincacc a0, a2, a5, zero # CHECK-ERROR: too many operands for instruction

#
# Generated on Fri, 04 Jul 2025 07:56:07 +0200.
#
# This file contains the Info for generating invalid tests for the XExample
# core architecture.



# RUN: not llvm-mc -triple=riscv32 --mattr=+xexample %s 2>&1\# RUN:        | FileCheck %s --check-prefixes=CHECK-ERROR

    
xexample.subincacc 0, a4, a7
# CHECK-ERROR: invalid operands for instruction

    
xexample.subincacc a1, 0, a7
# CHECK-ERROR: invalid operands for instruction

    
xexample.subincacc a1, a4, 0
# CHECK-ERROR: invalid operands for instruction

    
xexample.subincacc a1, a4
# CHECK-ERROR: too few operands for instruction

xexample.subincacc a4, a7
# CHECK-ERROR: too few operands for instruction
    

xexample.subincacc a1, a4, a7, zero
# CHECK-ERROR: too many operands for instruction

    


#
# Generated on Tue, 08 Jul 2025 09:42:51 +0200.
#
# This file contains the Info for generating invalid tests for the XExample
# core architecture.



# RUN: not llvm-mc -triple=riscv32 --mattr=+xexample %s 2>&1\# RUN:        | FileCheck %s --check-prefixes=CHECK-ERROR

    
xexample.subincacc 0, a5, a6
# CHECK-ERROR: invalid operands for instruction

    
xexample.subincacc a0, 0, a6
# CHECK-ERROR: invalid operands for instruction

    
xexample.subincacc a0, a5, 0
# CHECK-ERROR: invalid operands for instruction

    
xexample.subincacc a0, a5
# CHECK-ERROR: too few operands for instruction

xexample.subincacc a5, a6
# CHECK-ERROR: too few operands for instruction
    

xexample.subincacc a0, a5, a6, zero
# CHECK-ERROR: too many operands for instruction

    


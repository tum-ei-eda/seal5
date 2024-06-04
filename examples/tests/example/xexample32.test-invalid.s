# RUN: not llvm-mc -triple=riscv32 --mattr=+xexample %s 2>&1 \
# RUN:        | FileCheck %s --check-prefixes=CHECK-ERROR

xexample.subincacc a0, a1, 0 # CHECK-ERROR: invalid operand for instruction
xexample.subincacc a0, 0, a2 # CHECK-ERROR: invalid operand for instruction
xexample.subincacc 0, a1, a2 # CHECK-ERROR: invalid operand for instruction

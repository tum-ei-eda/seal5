# RUN: not llvm-mc -triple=riscv32 --mattr=+xcorevalu %s 2>&1 \
# RUN:        | FileCheck %s --check-prefixes=CHECK-ERROR

cv.abs t0, 0
# CHECK-ERROR: invalid operand for instruction

cv.abs 0, t1
# CHECK-ERROR: invalid operand for instruction

cv.abs t0
# CHECK-ERROR: too few operands for instruction

cv.abs t0, t1, t2
# CHECK-ERROR: invalid operand for instruction

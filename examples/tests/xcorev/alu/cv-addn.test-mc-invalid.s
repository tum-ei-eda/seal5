# RUN: not llvm-mc -triple=riscv32 --mattr=+xcorevalu %s 2>&1 \
# RUN:        | FileCheck %s --check-prefixes=CHECK-ERROR

seal5.cv.addN t0, t1, t2, -1
# CHECK-ERROR: immediate must be an integer in the range [0, 31]

seal5.cv.addN t0, t1, t2, 32
# CHECK-ERROR: immediate must be an integer in the range [0, 31]

seal5.cv.addN t0, t1, t2, a0
# CHECK-ERROR: immediate must be an integer in the range [0, 31]

seal5.cv.addN t0, t1, 0, 0
# CHECK-ERROR: invalid operand for instruction

seal5.cv.addN t0, 0, t2, 0
# CHECK-ERROR: invalid operand for instruction

seal5.cv.addN 0, t1, t2, 0
# CHECK-ERROR: invalid operand for instruction

seal5.cv.addN t0, t1, t2
# CHECK-ERROR: too few operands for instruction

seal5.cv.addN t0, t1, t2, 0, a0
# CHECK-ERROR: invalid operand for instruction

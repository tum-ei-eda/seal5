# RUN: not llvm-mc -triple=riscv32 --mattr=+xcorevmac %s 2>&1 \
# RUN:        | FileCheck %s --check-prefixes=CHECK-ERROR

cv.mac t0, t1, 0
# CHECK-ERROR: invalid operand for instruction

cv.mac t0, 0, t2
# CHECK-ERROR: invalid operand for instruction

cv.mac 0, t1, t2
# CHECK-ERROR: invalid operand for instruction

cv.mac t0, t1
# CHECK-ERROR: too few operands for instruction

cv.mac t0, t1, t2, t4
# CHECK-ERROR: invalid operand for instruction

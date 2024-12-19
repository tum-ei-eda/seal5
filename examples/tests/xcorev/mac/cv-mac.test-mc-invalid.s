# RUN: not llvm-mc -triple=riscv32 --mattr=+xcorevmac %s 2>&1 \
# RUN:        | FileCheck %s --check-prefixes=CHECK-ERROR

seal5.cv.mac t0, t1, 0
# CHECK-ERROR: invalid operand for instruction

seal5.cv.mac t0, 0, t2
# CHECK-ERROR: invalid operand for instruction

seal5.cv.mac 0, t1, t2
# CHECK-ERROR: invalid operand for instruction

seal5.cv.mac t0, t1
# CHECK-ERROR: too few operands for instruction

seal5.cv.mac t0, t1, t2, t4
# CHECK-ERROR: invalid operand for instruction

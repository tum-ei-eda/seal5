# RUN: llvm-mc -triple=riscv32 -mattr=+xcorevmem -show-encoding %s | FileCheck %s

seal5.cv.lw t0, (t1), 4
# CHECK: seal5.cv.lw t0, (t1), 4
# CHECK-SAME: encoding:
seal5.cv.lw t0, (t1), t2
# CHECK: seal5.cv.lw t0, (t1), t2
# CHECK-SAME: encoding:
seal5.cv.sw t0, (t1), 4
# CHECK: seal5.cv.sw t0, (t1), 4
# CHECK-SAME: encoding:
seal5.cv.sw t0, (t1), t2
# CHECK: seal5.cv.sw t0, (t1), t2
# CHECK-SAME: encoding:

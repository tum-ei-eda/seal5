# RUN: llvm-mc -triple=riscv32 -mattr=+xcorevbi -show-encoding %s | FileCheck %s

seal5.cv.beqimm t0, 5, 8
# CHECK: seal5.cv.beqimm
# CHECK-SAME: encoding:
seal5.cv.bneimm t0, -1, 8
# CHECK: seal5.cv.bneimm
# CHECK-SAME: encoding:

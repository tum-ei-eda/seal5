# RUN: not llvm-mc -triple=riscv32 -mattr=+xnormalize32 %s 2>&1 | FileCheck %s

xnormalize32.beqi5 a0, -17, 8
# CHECK: error: immediate must be an integer in the range [-16, 15]
xnormalize32.beqi5 a0, 16, 8
# CHECK: error: immediate must be an integer in the range [-16, 15]
xnormalize32.bltui3 a0, 8, 8
# CHECK: error: immediate must be an integer in the range [0, 7]
xnormalize32.bnei8 a0, -129, 8
# CHECK: error: immediate must be an integer in the range [-128, 127]
xnormalize32.bnei8 a0, 128, 8
# CHECK: error: immediate must be an integer in the range [-128, 127]

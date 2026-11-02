# RUN: llvm-mc -triple=riscv32 -mattr=+xnormalize32 -show-encoding %s | FileCheck %s
# RUN: llvm-mc -triple=riscv32 -mattr=+xnormalize32 -filetype=obj %s -o %t
# RUN: llvm-objdump -d --mattr=+xnormalize32 %t | FileCheck %s --check-prefix=DIS

xnormalize32.beqi5 a0, -16, 8
# CHECK: xnormalize32.beqi5 a0, -16, 8
# CHECK-SAME: encoding: [0x2b,0x34,0x05,0x01]
# DIS: xnormalize32.beqi5 a0, -0x10,
xnormalize32.bltui3 a0, 7, 8
# CHECK: xnormalize32.bltui3 a0, 7, 8
# CHECK-SAME: encoding: [0x2b,0x44,0xf5,0x01]
# DIS: xnormalize32.bltui3 a0, 0x7,
xnormalize32.bnei8 a0, -128, 8
# CHECK: xnormalize32.bnei8 a0, -128, 8
# CHECK-SAME: encoding: [0x5b,0x04,0x05,0x01]
# DIS: xnormalize32.bnei8 a0, -0x80,
xnormalize32.bnei8 a0, 127, 8
# CHECK: xnormalize32.bnei8 a0, 127, 8
# CHECK-SAME: encoding: [0x5b,0x74,0xf5,0x00]
# DIS: xnormalize32.bnei8 a0, 0x7f,

# RUN: llvm-mc -triple=riscv32 -mattr=+xnormalize32 -show-encoding %s | FileCheck %s
# RUN: llvm-mc -triple=riscv32 -mattr=+xnormalize32 -filetype=obj %s -o %t
# RUN: llvm-objdump -d --mattr=+xnormalize32 %t | FileCheck %s --check-prefix=DIS

xnormalize32.extract a0, a1, 8
# CHECK: xnormalize32.extract a0, a1, 8
# CHECK-SAME: encoding: [0x0b,0x85,0x85,0x40]
# DIS: xnormalize32.extract a0, a1, 0x8
xnormalize32.extract4 a0, a1, 8
# CHECK: xnormalize32.extract4 a0, a1, 8
# CHECK-SAME: encoding: [0x0b,0x85,0x85,0x42]
# DIS: xnormalize32.extract4 a0, a1, 0x8
xnormalize32.load16 a0, a1
# CHECK: xnormalize32.load16 a0, a1
# CHECK-SAME: encoding: [0x0b,0x95,0x05,0x40]
# DIS: xnormalize32.load16 a0, a1
xnormalize32.loadx a0, a1
# CHECK: xnormalize32.loadx a0, a1
# CHECK-SAME: encoding: [0x0b,0x95,0x15,0x40]
# DIS: xnormalize32.loadx a0, a1
xnormalize32.store16 a0, a1
# CHECK: xnormalize32.store16 a0, a1
# CHECK-SAME: encoding: [0x0b,0x90,0xa5,0x44]
# DIS: xnormalize32.store16 a0, a1
xnormalize32.load8 a0, a1
# CHECK: xnormalize32.load8 a0, a1
# CHECK-SAME: encoding: [0x0b,0x95,0x25,0x40]
# DIS: xnormalize32.load8 a0, a1
xnormalize32.branch a0, a1, 8
# CHECK: xnormalize32.branch a0, a1, 8
# CHECK-SAME: encoding: [0x2b,0x24,0xb5,0x00]
# DIS: xnormalize32.branch a0, a1, 0x20

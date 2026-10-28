# RUN: llvm-mc -triple=riscv64 -mattr=+xnormalize64 -show-encoding %s | FileCheck %s
# RUN: llvm-mc -triple=riscv64 -mattr=+xnormalize64 -filetype=obj %s -o %t
# RUN: llvm-objdump -d --mattr=+xnormalize64 %t | FileCheck %s --check-prefix=DIS

xnormalize64.wordnand a0, a1, a2
# CHECK: xnormalize64.wordnand a0, a1, a2
# CHECK-SAME: encoding: [0x0b,0xa5,0xc5,0x40]
# DIS: xnormalize64.wordnand a0, a1, a2
xnormalize64.wordnor a0, a1, a2
# CHECK: xnormalize64.wordnor a0, a1, a2
# CHECK-SAME: encoding: [0x0b,0xa5,0xc5,0x42]
# DIS: xnormalize64.wordnor a0, a1, a2
xnormalize64.load64 a0, a1
# CHECK: xnormalize64.load64 a0, a1
# CHECK-SAME: encoding: [0x0b,0x95,0x35,0x40]
# DIS: xnormalize64.load64 a0, a1
xnormalize64.load32 a0, a1
# CHECK: xnormalize64.load32 a0, a1
# CHECK-SAME: encoding: [0x0b,0x95,0x45,0x40]
# DIS: xnormalize64.load32 a0, a1

# RUN: llvm-mc -triple=riscv32 --mattr=+xopenasipbase -show-encoding %s \
# RUN:        | FileCheck %s --check-prefixes=CHECK-ENCODING,CHECK-INSTR

openasip_base_maxu t0, t1, t2
# CHECK-INSTR: openasip_base_maxu t0, t1, t2
# CHECK-ENCODING: [0x8b,0x02,0x73,0x2e]

openasip_base_maxu a0, a1, a2
# CHECK-INSTR: openasip_base_maxu a0, a1, a2
# CHECK-ENCODING: [0x0b,0x85,0xc5,0x2e]

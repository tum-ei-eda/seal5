# RUN: llvm-mc -triple=riscv32 --mattr=+xcorevbitmanip -show-encoding %s \
# RUN:        | FileCheck %s --check-prefixes=CHECK-ENCODING,CHECK-INSTR

seal5.cv.ror t0, t1, t2
# CHECK-INSTR: seal5.cv.ror t0, t1, t2
# CHECK-ENCODING: [0xab,0x32,0x73,0x40]

seal5.cv.ror a0, a1, a2
# CHECK-INSTR: seal5.cv.ror a0, a1, a2
# CHECK-ENCODING: [0x2b,0xb5,0xc5,0x40]

seal5.cv.ror s0, s1, s2
# CHECK-INSTR: seal5.cv.ror s0, s1, s2
# CHECK-ENCODING: [0x2b,0xb4,0x24,0x41]

# RUN: llvm-mc -triple=riscv32 --mattr=+xcorevalu -show-encoding %s \
# RUN:        | FileCheck %s --check-prefixes=CHECK-ENCODING,CHECK-INSTR

seal5.cv.adduRNr t0, t1, t2
# CHECK-INSTR: seal5.cv.adduRNr t0, t1, t2
# CHECK-ENCODING: [0xab,0x32,0x73,0x86]

seal5.cv.adduRNr a0, a1, a2
# CHECK-INSTR: seal5.cv.adduRNr a0, a1, a2
# CHECK-ENCODING: [0x2b,0xb5,0xc5,0x86]

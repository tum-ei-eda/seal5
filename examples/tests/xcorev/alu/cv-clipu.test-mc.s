# RUN: llvm-mc -triple=riscv32 --mattr=+xcorevalu -show-encoding %s \
# RUN:        | FileCheck %s --check-prefixes=CHECK-ENCODING,CHECK-INSTR

seal5.cv.clipu t0, t1, 0
# CHECK-INSTR: seal5.cv.clipu t0, t1, 0
# CHECK-ENCODING: [0xab,0x32,0x03,0x72]

seal5.cv.clipu t0, t1, 16
# CHECK-INSTR: seal5.cv.clipu t0, t1, 16
# CHECK-ENCODING: [0xab,0x32,0x03,0x73]

seal5.cv.clipu a0, zero, 31
# CHECK-INSTR: seal5.cv.clipu a0, zero, 31
# CHECK-ENCODING: [0x2b,0x35,0xf0,0x73]

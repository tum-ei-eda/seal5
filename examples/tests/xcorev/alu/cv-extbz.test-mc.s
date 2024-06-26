# RUN: llvm-mc -triple=riscv32 --mattr=+xcorevalu -show-encoding %s \
# RUN:        | FileCheck %s --check-prefixes=CHECK-ENCODING,CHECK-INSTR

seal5.cv.extbz t0, t1
# CHECK-INSTR: seal5.cv.extbz t0, t1
# CHECK-ENCODING: [0xab,0x32,0x03,0x66]

seal5.cv.extbz a0, a1
# CHECK-INSTR: seal5.cv.extbz a0, a1
# CHECK-ENCODING: [0x2b,0xb5,0x05,0x66]

# RUN: sed -e 's/seal5\.//g; s/cv\.sletu/cv.sleu/g; s/cv\.slet/cv.sle/g' %s | llvm-mc -triple=riscv32 -mattr=+xcvalu -show-encoding | FileCheck %s --check-prefix=NATIVE
# RUN: llvm-mc -triple=riscv32 --mattr=+xcorevalu -show-encoding %s \
# RUN:        | FileCheck %s --check-prefixes=CHECK-ENCODING,CHECK-INSTR

seal5.cv.addRN t0, t1, t2, 0
# CHECK-INSTR: seal5.cv.addRN t0, t1, t2, 0
# CHECK-ENCODING: [0xdb,0x22,0x73,0x80]

seal5.cv.addRN t0, t1, t2, 16
# CHECK-INSTR: seal5.cv.addRN t0, t1, t2, 16
# CHECK-ENCODING: [0xdb,0x22,0x73,0xa0]

seal5.cv.addRN a0, a1, zero, 31
# CHECK-INSTR: seal5.cv.addRN a0, a1, zero, 31
# CHECK-ENCODING: [0x5b,0xa5,0x05,0xbe]

# NATIVE: encoding: [0xdb,0x22,0x73,0x80]
# NATIVE: encoding: [0xdb,0x22,0x73,0xa0]
# NATIVE: encoding: [0x5b,0xa5,0x05,0xbe]

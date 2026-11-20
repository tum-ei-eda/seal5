# RUN: sed -e 's/seal5\.//g; s/cv\.sletu/cv.sleu/g; s/cv\.slet/cv.sle/g' %s | llvm-mc -triple=riscv32 -mattr=+xcvalu -show-encoding | FileCheck %s --check-prefix=NATIVE
# RUN: llvm-mc -triple=riscv32 --mattr=+xcorevalu -show-encoding %s \
# RUN:        | FileCheck %s --check-prefixes=CHECK-ENCODING,CHECK-INSTR

seal5.cv.clipur t0, t1, t2
# CHECK-INSTR: seal5.cv.clipur t0, t1, t2
# CHECK-ENCODING: [0xab,0x32,0x73,0x76]

seal5.cv.clipur a0, a1, a2
# CHECK-INSTR: seal5.cv.clipur a0, a1, a2
# CHECK-ENCODING: [0x2b,0xb5,0xc5,0x76]

# NATIVE: encoding: [0xab,0x32,0x73,0x76]
# NATIVE: encoding: [0x2b,0xb5,0xc5,0x76]

# RUN: sed -e 's/seal5\.//g; s/cv\.sletu/cv.sleu/g; s/cv\.slet/cv.sle/g' %s | llvm-mc -triple=riscv32 -mattr=+xcvalu -show-encoding | FileCheck %s --check-prefix=NATIVE
# RUN: llvm-mc -triple=riscv32 -mattr=+xcorevalu -show-encoding %s | FileCheck %s

seal5.cv.subN x5, x6, x7, 0
# CHECK: seal5.cv.subN
# CHECK-SAME: encoding: [0xdb,0x32,0x73,0x00]

# NATIVE: encoding: [0xdb,0x32,0x73,0x00]

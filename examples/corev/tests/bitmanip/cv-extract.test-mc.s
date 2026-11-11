# RUN: sed -e 's/seal5\.//g; s/cv\.sletu/cv.sleu/g; s/cv\.slet/cv.sle/g' %s | llvm-mc -triple=riscv32 -mattr=+xcvbitmanip -show-encoding | FileCheck %s --check-prefix=NATIVE
# RUN: llvm-mc -triple=riscv32 -mattr=+xcorevbitmanip -show-encoding %s | FileCheck %s

seal5.cv.extract x5, x6, 0, 0
# CHECK: seal5.cv.extract
# CHECK-SAME: encoding: [0xdb,0x02,0x03,0x00]

# NATIVE: encoding: [0xdb,0x02,0x03,0x00]

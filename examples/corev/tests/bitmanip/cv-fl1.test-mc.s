# RUN: sed -e 's/seal5\.//g; s/cv\.sletu/cv.sleu/g; s/cv\.slet/cv.sle/g' %s | llvm-mc -triple=riscv32 -mattr=+xcvbitmanip -show-encoding | FileCheck %s --check-prefix=NATIVE
# RUN: llvm-mc -triple=riscv32 -mattr=+xcorevbitmanip -show-encoding %s | FileCheck %s

seal5.cv.fl1 x5, x6
# CHECK: seal5.cv.fl1
# CHECK-SAME: encoding: [0xab,0x32,0x03,0x44]

# NATIVE: encoding: [0xab,0x32,0x03,0x44]

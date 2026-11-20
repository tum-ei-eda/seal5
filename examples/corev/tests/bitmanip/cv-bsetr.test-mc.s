# RUN: sed -e 's/seal5\.//g; s/cv\.sletu/cv.sleu/g; s/cv\.slet/cv.sle/g' %s | llvm-mc -triple=riscv32 -mattr=+xcvbitmanip -show-encoding | FileCheck %s --check-prefix=NATIVE
# RUN: llvm-mc -triple=riscv32 -mattr=+xcorevbitmanip -show-encoding %s | FileCheck %s

seal5.cv.bsetr x5, x6, x7
# CHECK: seal5.cv.bsetr
# CHECK-SAME: encoding: [0xab,0x32,0x73,0x3a]

# NATIVE: encoding: [0xab,0x32,0x73,0x3a]

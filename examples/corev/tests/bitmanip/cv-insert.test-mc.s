# RUN: sed -e 's/seal5\.//g; s/cv\.sletu/cv.sleu/g; s/cv\.slet/cv.sle/g' %s | llvm-mc -triple=riscv32 -mattr=+xcvbitmanip -show-encoding | FileCheck %s --check-prefix=NATIVE
# RUN: llvm-mc -triple=riscv32 -mattr=+xcorevbitmanip -show-encoding %s | FileCheck %s

seal5.cv.insert x5, x6, 0, 0
# CHECK: seal5.cv.insert
# CHECK-SAME: encoding: [0xdb,0x02,0x03,0x80]

# NATIVE: encoding: [0xdb,0x02,0x03,0x80]

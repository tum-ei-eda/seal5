# RUN: sed -e 's/seal5\.//g; s/cv\.sletu/cv.sleu/g; s/cv\.slet/cv.sle/g' %s | llvm-mc -triple=riscv32 -mattr=+xcvbi -show-encoding | FileCheck %s --check-prefix=NATIVE
# RUN: llvm-mc -triple=riscv32 -mattr=+xcorevbi -show-encoding %s | FileCheck %s

seal5.cv.beqimm x6, 0, 0
# CHECK: seal5.cv.beqimm
# CHECK-SAME: encoding: [0x0b,0x60,0x03,0x00]

# NATIVE: encoding: [0x0b,0x60,0x03,0x00]

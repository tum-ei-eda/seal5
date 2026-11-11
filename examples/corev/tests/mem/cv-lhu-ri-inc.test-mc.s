# RUN: sed -e 's/seal5\.//g; s/cv\.sletu/cv.sleu/g; s/cv\.slet/cv.sle/g' %s | llvm-mc -triple=riscv32 -mattr=+xcvmem -show-encoding | FileCheck %s --check-prefix=NATIVE
# RUN: llvm-mc -triple=riscv32 -mattr=+xcorevmem -show-encoding %s | FileCheck %s

seal5.cv.lhu x5, (x6), 0
# CHECK: seal5.cv.lhu
# CHECK-SAME: encoding: [0x8b,0x52,0x03,0x00]

# NATIVE: encoding: [0x8b,0x52,0x03,0x00]

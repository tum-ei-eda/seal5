# RUN: sed -e 's/seal5\.//g; s/cv\.sletu/cv.sleu/g; s/cv\.slet/cv.sle/g' %s | llvm-mc -triple=riscv32 -mattr=+xcvmem -show-encoding | FileCheck %s --check-prefix=NATIVE
# RUN: llvm-mc -triple=riscv32 -mattr=+xcorevmem -show-encoding %s | FileCheck %s

seal5.cv.sw x7, x28(x6)
# CHECK: seal5.cv.sw
# CHECK-SAME: encoding: [0x2b,0x3e,0x73,0x2c]

# NATIVE: encoding: [0x2b,0x3e,0x73,0x2c]

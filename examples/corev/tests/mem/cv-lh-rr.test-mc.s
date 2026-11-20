# RUN: sed -e 's/seal5\.//g; s/cv\.sletu/cv.sleu/g; s/cv\.slet/cv.sle/g' %s | llvm-mc -triple=riscv32 -mattr=+xcvmem -show-encoding | FileCheck %s --check-prefix=NATIVE
# RUN: llvm-mc -triple=riscv32 -mattr=+xcorevmem -show-encoding %s | FileCheck %s

seal5.cv.lh x5, x7(x6)
# CHECK: seal5.cv.lh
# CHECK-SAME: encoding: [0xab,0x32,0x73,0x0a]

# NATIVE: encoding: [0xab,0x32,0x73,0x0a]

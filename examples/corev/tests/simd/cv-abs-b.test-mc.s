# RUN: sed -e 's/seal5\.//g; s/cv\.sletu/cv.sleu/g; s/cv\.slet/cv.sle/g' %s | llvm-mc -triple=riscv32 -mattr=+xcvsimd -show-encoding | FileCheck %s --check-prefix=NATIVE
# RUN: llvm-mc -triple=riscv32 -mattr=+xcorevsimd -show-encoding %s | FileCheck %s

seal5.cv.abs.b x5, x6
# CHECK: seal5.cv.abs.b
# CHECK-SAME: encoding: [0xfb,0x12,0x03,0x70]

# NATIVE: encoding: [0xfb,0x12,0x03,0x70]

# RUN: sed -e 's/seal5\.//g; s/cv\.sletu/cv.sleu/g; s/cv\.slet/cv.sle/g' %s | llvm-mc -triple=riscv32 -mattr=+xcvsimd -show-encoding | FileCheck %s --check-prefix=NATIVE
# RUN: llvm-mc -triple=riscv32 -mattr=+xcorevsimd -show-encoding %s | FileCheck %s

seal5.cv.cmpltu.sc.h x5, x6, x7
# CHECK: seal5.cv.cmpltu.sc.h
# CHECK-SAME: encoding: [0xfb,0x42,0x73,0x44]

# NATIVE: encoding: [0xfb,0x42,0x73,0x44]

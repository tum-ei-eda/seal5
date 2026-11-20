# RUN: sed -e 's/seal5\.//g; s/cv\.sletu/cv.sleu/g; s/cv\.slet/cv.sle/g' %s | llvm-mc -triple=riscv32 -mattr=+xcvmac -show-encoding | FileCheck %s --check-prefix=NATIVE
# RUN: llvm-mc -triple=riscv32 -mattr=+xcorevmac -show-encoding %s | FileCheck %s

seal5.cv.mulhhsn x5, x6, x7, 0
# CHECK: seal5.cv.mulhhsn
# CHECK-SAME: encoding: [0xdb,0x42,0x73,0x40]

# NATIVE: encoding: [0xdb,0x42,0x73,0x40]

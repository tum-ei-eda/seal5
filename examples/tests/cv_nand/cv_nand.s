# RUN: llvm-mc %s -triple=riscv32 -mattr=+xcorevnand -riscv-no-aliases -show-encoding \
# RUN:     | FileCheck -check-prefixes=CHECK-ASM,CHECK-ASM-AND-OBJ %s
# RUN: llvm-mc -filetype=obj -triple=riscv32 -mattr=+xcorevnand < %s \
# RUN:     | llvm-objdump --mattr=+xcorevnand -M no-aliases -d -r - \
# RUN:     | FileCheck --check-prefix=CHECK-ASM-AND-OBJ %s

# CHECK-ASM-AND-OBJ: cv.nand.bitwise a4, ra, s0
# CHECK-ASM: encoding: [0x2b,0xe7,0x80,0x92]
cv.nand.bitwise a4, ra, s0

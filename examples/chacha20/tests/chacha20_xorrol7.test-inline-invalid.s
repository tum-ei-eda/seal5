# RUN: not llvm-mc -triple=riscv32 --mattr=+xchacha %s 2>&1 \
# RUN:        | FileCheck %s --check-prefixes=CHECK-ERROR

# CHECK-ERROR: invalid operand for instruction
chacha.xorrol7 3, 4, 5

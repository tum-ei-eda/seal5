# RUN: not llvm-mc -triple=riscv32 --mattr=+xs4emac %s 2>&1 \
# RUN:        | FileCheck %s --check-prefixes=CHECK-ERROR

# CHECK-ERROR: invalid operand for instruction
s4e.macs_32 0, a7

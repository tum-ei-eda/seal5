# RUN: not llvm-mc -triple=riscv32 --mattr=+xopenasipbase %s 2>&1 \
# RUN:        | FileCheck %s --check-prefixes=CHECK-ERROR

openasip_base_max a0, a1, 0 # CHECK-ERROR: invalid operand for instruction
openasip_base_max a0, 0, a2 # CHECK-ERROR: invalid operand for instruction
openasip_base_max 0, a1, a2 # CHECK-ERROR: invalid operand for instruction

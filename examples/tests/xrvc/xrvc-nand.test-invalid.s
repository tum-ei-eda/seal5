# RUN: not llvm-mc -triple=riscv32 --mattr=+xrvc %s 2>&1 \
# RUN:        | FileCheck %s --check-prefixes=CHECK-ERROR

xrv.nand a0, a1, 0 # CHECK-ERROR: invalid operand for instruction

xrvc.nand a0, 0 # CHECK-ERROR: invalid operand for instruction

# RUN: not llvm-mc -triple=riscv32 --mattr=+xrvc %s 2>&1 \
# RUN:        | FileCheck %s --check-prefixes=CHECK-ERROR

xrvc.nandi a0, 36 # CHECK-ERROR: immediate must be an integer in the range [-32, 31]

xrvc.nandi a0, a1 # CHECK-ERROR: immediate must be an integer in the range [-32, 31]

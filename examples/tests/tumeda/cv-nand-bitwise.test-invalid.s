# RUN: not llvm-mc -triple riscv32 -mattr=+m < %s 2>&1 | FileCheck %s

cv.nand.bitwise a4, ra, s0 # CHECK: :[[@LINE]]:1: error: instruction requires the following: 'XCoreVNand' (XCoreVNand Extension)

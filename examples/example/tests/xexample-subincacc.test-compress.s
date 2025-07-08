# Generated on Tue, 08 Jul 2025 09:42:51 +0200.
#
# This file contains the Info for generating invalid tests for the XExample 
# core architecture.



# RUN: llvm-mc -triple riscv32 -mattr=+xexample -show-encoding # RUN:   -riscv-no-aliases < %s | FileCheck -check-prefixes=CHECK,CHECK-INST %s

# CHECK-INST: xexample.subincacc s0, 14
# CHECK: # encoding: [0x38,0x88]
xexample.subincacc s0, s0, 14

// TODO: add commutativity pattern
// xexample.subincacc s0, 14, s0

# RUN: llvm-mc -triple riscv32 -mattr=+xrvc -show-encoding \
# RUN:   -riscv-no-aliases < %s | FileCheck -check-prefixes=CHECK,CHECK-INST %s

# CHECK-INST: xrvc.nand s0, a5
# CHECK: # encoding: [0x7d,0x9c]
xrv.nand s0, s0, a5

// TODO: add commutativity pattern
// xrv.nand s0, a5, s0

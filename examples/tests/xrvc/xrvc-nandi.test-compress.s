# RUN: llvm-mc -triple riscv32 -mattr=+xrvc -show-encoding \
# RUN:   -riscv-no-aliases < %s | FileCheck -check-prefixes=CHECK,CHECK-INST %s

# CHECK-INST: xrvc.nandi s0, 14
# CHECK: # encoding: [0x38,0x88]
xrv.nandi s0, s0, 14

// TODO: add commutativity pattern
// xrv.nandi s0, 14, s0

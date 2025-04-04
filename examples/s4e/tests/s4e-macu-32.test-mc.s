# RUN: llvm-mc -triple=riscv32 --mattr=+xs4emac -show-encoding %s \
# RUN:        | FileCheck %s --check-prefixes=CHECK-ENCODING,CHECK-INSTR
# RUN: not llvm-mc -triple riscv32 %s 2>&1 \
# RUN:     | FileCheck -check-prefix=CHECK-NO-EXT %s

# CHECK-INSTR: s4e.macu_32 s5, a7
# CHECK-ENCODING: [0x0b,0x90,0x1a,0x01]
# CHECK-NO-EXT: instruction requires the following: 'XS4EMAC' (X_S4E_MAC Extension){{$}}
s4e.macu_32 s5, a7

# MC test of sample S4E MAC instruction extensions

# RUN: llvm-mc -triple=riscv32 --mattr=+xs4emac -show-encoding %s \
# RUN:        | FileCheck %s --check-prefixes=CHECK-ENCODING,CHECK-INSTR
# RUN: not llvm-mc -triple riscv32 %s 2>&1 \
# RUN:     | FileCheck -check-prefix=CHECK-NO-EXT %s

s4e.reset_acc
# CHECK-INSTR: s4e.reset_acc
# CHECK-ENCODING: [0x0b,0x00,0x00,0x00]
# CHECK-NO-EXT: instruction requires the following: 'XS4EMAC' (X_S4E_MAC Extension){{$}}

s4e.get_acc_lo t1
# CHECK-INSTR: s4e.get_acc_lo t1
# CHECK-ENCODING: [0x0b,0x03,0x00,0x02]
# CHECK-NO-EXT: instruction requires the following: 'XS4EMAC' (X_S4E_MAC Extension){{$}}

s4e.get_acc_hi s9
# CHECK-INSTR: s4e.get_acc_hi s9
# CHECK-ENCODING: [0x8b,0x0c,0x00,0x04]
# CHECK-NO-EXT: instruction requires the following: 'XS4EMAC' (X_S4E_MAC Extension){{$}}

s4e.macu_32 s5, a7
# CHECK-INSTR: s4e.macu_32 s5, a7
# CHECK-ENCODING: [0x0b,0x90,0x1a,0x01]
# CHECK-NO-EXT: instruction requires the following: 'XS4EMAC' (X_S4E_MAC Extension){{$}}

s4e.macs_32 s5, a7
# CHECK-INSTR: s4e.macs_32 s5, a7
# CHECK-ENCODING: [0x0b,0x90,0x1a,0x03]
# CHECK-NO-EXT: instruction requires the following: 'XS4EMAC' (X_S4E_MAC Extension){{$}}

s4e.macu_64 s5, a7
# CHECK-INSTR: s4e.macu_64 s5, a7
# CHECK-ENCODING: [0x0b,0xa0,0x1a,0x01]
# CHECK-NO-EXT: instruction requires the following: 'XS4EMAC' (X_S4E_MAC Extension){{$}}

s4e.macs_64 s5, a7
# CHECK-INSTR: s4e.macs_64 s5, a7
# CHECK-ENCODING: [0x0b,0xa0,0x1a,0x03]
# CHECK-NO-EXT: instruction requires the following: 'XS4EMAC' (X_S4E_MAC Extension){{$}}

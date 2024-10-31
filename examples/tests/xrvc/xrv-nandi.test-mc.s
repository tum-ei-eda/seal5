# RUN: llvm-mc -triple=riscv32 --mattr=+xrvc -show-encoding -riscv-no-aliases %s \
# RUN:        | FileCheck %s --check-prefixes=CHECK-ENCODING,CHECK-INSTR
# RUN: not llvm-mc -triple riscv32 %s 2>&1 \
# RUN:     | FileCheck -check-prefix=CHECK-NO-EXT %s

xrv.nandi a1, a2, 14
# CHECK-INSTR: xrv.nandi a1, a2, 14
# CHECK-ENCODING: [0x8b,0x75,0xe6,0x00]
# CHECK-NO-EXT: instruction requires the following: 'XRVC' (XRVC Extension){{$}}

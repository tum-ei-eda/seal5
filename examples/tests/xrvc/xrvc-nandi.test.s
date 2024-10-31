# RUN: llvm-mc -triple=riscv32 --mattr=+xrvc -show-encoding -riscv-no-aliases %s \
# RUN:        | FileCheck %s --check-prefixes=CHECK-ENCODING,CHECK-INSTR
# RUN: not llvm-mc -triple riscv32 %s 2>&1 \
# RUN:     | FileCheck -check-prefix=CHECK-NO-EXT %s

xrvc.nandi a1, 14
# CHECK-INSTR: xrvc.nandi a1, 14
# CHECK-ENCODING: [0xb8,0x89]
# CHECK-NO-EXT: instruction requires the following: 'XRVC' (XRVC Extension){{$}}

# RUN: llvm-mc -triple=riscv32 --mattr=+xrvc -show-encoding -riscv-no-aliases %s \
# RUN:        | FileCheck %s --check-prefixes=CHECK-ENCODING,CHECK-INSTR
# RUN: not llvm-mc -triple riscv32 %s 2>&1 \
# RUN:     | FileCheck -check-prefix=CHECK-NO-EXT %s

xrv.nand a1, a2, a3
# CHECK-INSTR: xrv.nand a1, a2, a3
# CHECK-ENCODING: [0xab,0x65,0xd6,0x92]
# CHECK-NO-EXT: instruction requires the following: 'XRVC' (XRVC Extension){{$}}

# RUN: llvm-mc -triple=riscv32 --mattr=+xrvc -show-encoding -riscv-no-aliases %s \
# RUN:        | FileCheck %s --check-prefixes=CHECK-ENCODING,CHECK-INSTR
# RUN: not llvm-mc -triple riscv32 %s 2>&1 \
# RUN:     | FileCheck -check-prefix=CHECK-NO-EXT %s

xrvc.nand a1, a2
# CHECK-INSTR: xrvc.nand a1, a2
# CHECK-ENCODING: [0xf1,0x9d]
# CHECK-NO-EXT: instruction requires the following: 'XRVC' (XRVC Extension){{$}}

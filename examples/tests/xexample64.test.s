# RUN: llvm-mc -triple=riscv64 --mattr=+xexample -show-encoding %s \
# RUN:        | FileCheck %s --check-prefixes=CHECK-ENCODING,CHECK-INSTR
# RUN: not llvm-mc -triple riscv64 %s 2>&1 \
# RUN:     | FileCheck -check-prefix=CHECK-NO-EXT %s

xexample.subincacc a1, a2, a3
# CHECK-INSTR: xexample.subincacc a1, a2, a3
# CHECK-ENCODING: [0xf1,0x9d,0x00,0x00]
# CHECK-NO-EXT: instruction requires the following: 'XRVC' (XRVC Extension){{$}}

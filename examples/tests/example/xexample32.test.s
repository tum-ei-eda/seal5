# RUN: llvm-mc -triple=riscv32 --mattr=+xexample -show-encoding %s \
# RUN:        | FileCheck %s --check-prefixes=CHECK-ENCODING,CHECK-INSTR
# RUN: not llvm-mc -triple riscv32 %s 2>&1 \
# RUN:     | FileCheck -check-prefix=CHECK-NO-EXT %s

xexample.subincacc a1, a2, a3
# CHECK-INSTR: xexample.subincacc a1, a2, a3
# CHECK-ENCODING: [0xab,0x35,0xd6,0x50]
# CHECK-NO-EXT: instruction requires the following: 'XExample' (XExample Extension){{$}}

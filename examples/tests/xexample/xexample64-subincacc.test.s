# RUN: llvm-mc -triple=riscv64 --mattr=+xexample -show-encoding %s \
# RUN:        | FileCheck %s --check-prefixes=CHECK-ENCODING,CHECK-INSTR
# RUN: not llvm-mc -triple riscv64 %s 2>&1 \
# RUN:     | FileCheck -check-prefix=CHECK-NO-EXT %s

xexample64.subincacc a1, a2, a3
# CHECK-INSTR: xexample64.subincacc a1, a2, a3
# CHECK-ENCODING: [0xab,0x35,0xd6,0x50]
# CHECK-NO-EXT: instruction requires the following: 'XExample' (XExample64 Extension){{$}}

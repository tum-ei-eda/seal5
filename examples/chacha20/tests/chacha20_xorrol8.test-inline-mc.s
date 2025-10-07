# RUN: llvm-mc -triple=riscv32 --mattr=+xchacha -show-encoding -M numeric %s \
# RUN:        | FileCheck %s --check-prefixes=CHECK-ENCODING,CHECK-INSTR
# RUN: not llvm-mc -triple riscv32 %s 2>&1 \
# RUN:     | FileCheck -check-prefix=CHECK-NO-EXT %s

# CHECK-INSTR: chacha.xorrol8 x3, x4, x5
# CHECK-ENCODING: [0x8b,0x21,0x52,0x00]
# CHECK-NO-EXT: instruction requires the following: 'XCHACHA' (XCHACHA Extension){{$}}
chacha.xorrol8 x3, x4, x5

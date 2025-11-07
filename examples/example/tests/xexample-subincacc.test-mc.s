# Generated on Mon, 14 Jul 2025 01:09:17 +0200.
#
# This file contains the Info for generating invalid tests for the XExample 
# core architecture.


# RUN: llvm-mc -triple=riscv32 --mattr=+xexample -show-encoding %s \
# RUN:        | FileCheck %s --check-prefixes=CHECK-ENCODING,CHECK-INSTR
# RUN: not llvm-mc -triple riscv32 %s 2>&1 \
# RUN:     | FileCheck -check-prefix=CHECK-NO-EXT %s

xexample.subincacc a0, a2, a5
# CHECK-INSTR: xexample.subincacc a0, a2, a5
# CHECK-ENCODING: [0x2b,0x35,0xf6,0x50]

# CHECK-NO-EXT: instruction requires the following: 'XExample' (XExample Extension){{$}}

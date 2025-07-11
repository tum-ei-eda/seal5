# Generated on Tue, 08 Jul 2025 09:42:51 +0200.
#
# This file contains the Info for generating invalid tests for the XExample 
# core architecture.



# RUN: llvm-mc -triple=riscv32 --mattr=+xexample -show-encoding %s 
# RUN:        | FileCheck %s --check-prefixes=CHECK-ENCODING,CHECK-INSTR
# RUN: not llvm-mc -triple riscv32 %s 2>&1 \
# RUN:     | FileCheck -check-prefix=CHECK-NO-EXT %s

xexample.subincacc a0 , a5 , a6
# CHECK-INSTR: xexample.subincacc a0 , a5 , a6
# CHECK-ENCODING: [0x2b, 0xb5, 0x07, 0x51]

# CHECK-NO-EXT: instruction requires the following: 'XExample' (XExample32 Extension){{$}}

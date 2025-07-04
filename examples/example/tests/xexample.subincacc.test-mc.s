# Generated on Fri, 04 Jul 2025 07:56:07 +0200.
#
# This file contains the Info for generating invalid tests for the XExample 
# core architecture.



# RUN: llvm-mc -triple=riscv32 --mattr=+xexample -show-encoding %s # RUN:        | FileCheck %s --check-prefixes=CHECK-ENCODING,CHECK-INSTR
# RUN: not llvm-mc -triple riscv32 %s 2>&1 # RUN:     | FileCheck -check-prefix=CHECK-NO-EXT %s

xexample.subincacc a1 , a4 , a7
# CHECK-INSTR: xexample.subincacc a1 , a4 , a7
# CHECK-ENCODING: [0xab, 0x35, 0x17, 0x51]

# CHECK-NO-EXT: instruction requires the following: 'XExample' (XExample32 Extension){{$}}

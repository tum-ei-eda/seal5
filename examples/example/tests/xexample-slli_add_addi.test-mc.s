# Generated on Mon, 14 Jul 2025 01:09:17 +0200.
#
# This file contains the Info for generating invalid tests for the XExample 
# core architecture.


# RUN: not llvm-mc -triple=riscv32 --mattr=+xexample -show-encoding %s 2>&1 \
# RUN:        | FileCheck %s --check-prefixes=CHECK-ENCODING,CHECK-INSTR
# RUN: not llvm-mc -triple riscv32 %s 2>&1 \
# RUN:     | FileCheck -check-prefix=CHECK-NO-EXT %s

 
xexample.slli_add_addi a1, a4, a6, 0, 0
# CHECK-INSTR: xexample.slli_add_addi a1, a4, a6, 0, 0
# CHECK-ENCODING: [0x57,0x96,0x83,0x00]
 
xexample.slli_add_addi a1, a4, a6, 16, 0
# CHECK-INSTR: xexample.slli_add_addi a1, a4, a6, 16, 0
# CHECK-ENCODING: [0x57,0x96,0x83,0x10]
 
xexample.slli_add_addi a1, a4, a6, 31, 0
# CHECK-INSTR: xexample.slli_add_addi a1, a4, a6, 31, 0
# CHECK-ENCODING: [0x57,0x96,0x83,0x1f]
 
xexample.slli_add_addi a1, a4, a6, 11, 0
# CHECK-INSTR: xexample.slli_add_addi a1, a4, a6, 11, 0
# CHECK-ENCODING: [0x57,0x96,0x83,0x00]
 
xexample.slli_add_addi a1, a4, a6, 11, 4
# CHECK-INSTR: xexample.slli_add_addi a1, a4, a6, 11, 4
# CHECK-ENCODING: [0x57,0x96,0x83,0x80]
 
xexample.slli_add_addi a1, a4, a6, 11, 7
# CHECK-INSTR: xexample.slli_add_addi a1, a4, a6, 11, 7
# CHECK-ENCODING: [0x57,0x96,0x83,0xe0]
 
# CHECK-NO-EXT: instruction requires the following: 'XExample' (XExample Extension){{$}}

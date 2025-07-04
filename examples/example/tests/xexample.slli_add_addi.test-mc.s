# Generated on Fri, 04 Jul 2025 07:56:07 +0200.
#
# This file contains the Info for generating invalid tests for the XExample 
# core architecture.



# RUN: llvm-mc -triple=riscv32 --mattr=+xexample -show-encoding %s # RUN:        | FileCheck %s --check-prefixes=CHECK-ENCODING,CHECK-INSTR
# RUN: not llvm-mc -triple riscv32 %s 2>&1 # RUN:     | FileCheck -check-prefix=CHECK-NO-EXT %s

 
xexample.slli_add_addi a1, a5, a7, 0, 2
# CHECK-INSTR: xexample.slli_add_addi a1, a5, a7, 0, 2
# CHECK-ENCODING: [0x57, 0xd6, 0x8b, 0x00]
 
xexample.slli_add_addi a1, a5, a7, 16, 2
# CHECK-INSTR: xexample.slli_add_addi a1, a5, a7, 16, 2
# CHECK-ENCODING: [0x57, 0xd6, 0x8b, 0x10]
 
xexample.slli_add_addi a1, a5, a7, 31, 2
# CHECK-INSTR: xexample.slli_add_addi a1, a5, a7, 31, 2
# CHECK-ENCODING: [0x57, 0xd6, 0x8b, 0x1f]
 
xexample.slli_add_addi a1, a5, a7, 27, 0
# CHECK-INSTR: xexample.slli_add_addi a1, a5, a7, 27, 0
# CHECK-ENCODING: [0x57, 0xd6, 0x8b, 0x00]
 
xexample.slli_add_addi a1, a5, a7, 27, 4
# CHECK-INSTR: xexample.slli_add_addi a1, a5, a7, 27, 4
# CHECK-ENCODING: [0x57, 0xd6, 0x8b, 0x80]
 
xexample.slli_add_addi a1, a5, a7, 27, 7
# CHECK-INSTR: xexample.slli_add_addi a1, a5, a7, 27, 7
# CHECK-ENCODING: [0x57, 0xd6, 0x8b, 0xe0]
 
# CHECK-NO-EXT: instruction requires the following: 'XExample' (XExample32 Extension){{$}}

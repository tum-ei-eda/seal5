# Generated on Tue, 08 Jul 2025 09:42:51 +0200.
#
# This file contains the Info for generating invalid tests for the XExample 
# core architecture.



# RUN: llvm-mc -triple=riscv32 --mattr=+xexample -show-encoding %s # RUN:        | FileCheck %s --check-prefixes=CHECK-ENCODING,CHECK-INSTR
# RUN: not llvm-mc -triple riscv32 %s 2>&1 # RUN:     | FileCheck -check-prefix=CHECK-NO-EXT %s

 
xexample.slli_add_addi a0, a2, a7, 0, 3
# CHECK-INSTR: xexample.slli_add_addi a0, a2, a7, 0, 3
# CHECK-ENCODING: [0x57, 0x14, 0x8b, 0x00]
 
xexample.slli_add_addi a0, a2, a7, 16, 3
# CHECK-INSTR: xexample.slli_add_addi a0, a2, a7, 16, 3
# CHECK-ENCODING: [0x57, 0x14, 0x8b, 0x10]
 
xexample.slli_add_addi a0, a2, a7, 31, 3
# CHECK-INSTR: xexample.slli_add_addi a0, a2, a7, 31, 3
# CHECK-ENCODING: [0x57, 0x14, 0x8b, 0x1f]
 
xexample.slli_add_addi a0, a2, a7, 15, 0
# CHECK-INSTR: xexample.slli_add_addi a0, a2, a7, 15, 0
# CHECK-ENCODING: [0x57, 0x14, 0x8b, 0x00]
 
xexample.slli_add_addi a0, a2, a7, 15, 4
# CHECK-INSTR: xexample.slli_add_addi a0, a2, a7, 15, 4
# CHECK-ENCODING: [0x57, 0x14, 0x8b, 0x80]
 
xexample.slli_add_addi a0, a2, a7, 15, 7
# CHECK-INSTR: xexample.slli_add_addi a0, a2, a7, 15, 7
# CHECK-ENCODING: [0x57, 0x14, 0x8b, 0xe0]
 
# CHECK-NO-EXT: instruction requires the following: 'XExample' (XExample32 Extension){{$}}

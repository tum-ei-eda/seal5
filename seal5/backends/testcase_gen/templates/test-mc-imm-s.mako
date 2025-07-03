## SPDX-License-Identifier: Apache-2.0
##
## This file is part of the M2-ISA-R project: https://github.com/tum-ei-eda/M2-ISA-R
##
## Copyright (c) 2025 TUM Department of Electrical and Computer Engineering.
## Copyright (c) 2025 DLR-SE Department of System Evolution and Operation
\
# Generated on ${start_time}.
#
# This file contains the Info for generating invalid tests for the ${set_name} 
# core architecture.



# RUN: llvm-mc -triple=riscv${xlen} --mattr=+${arch} -show-encoding %s \
# RUN:        | FileCheck %s --check-prefixes=CHECK-ENCODING,CHECK-INSTR
# RUN: not llvm-mc -triple riscv${xlen} %s 2>&1 \
# RUN:     | FileCheck -check-prefix=CHECK-NO-EXT %s

 % for loop_cnt, (op_str, enc_str) in enumerate(zip(instr_op_str, enc)):  
 
${mnemonic} ${', '.join(op_str[0:len(op_str)])}
# CHECK-INSTR: ${mnemonic} ${', '.join(op_str[0:len(op_str)])}
# CHECK-ENCODING: [${enc_str}]
 % endfor
 
# CHECK-NO-EXT: instruction requires the following: '${set_name}' (${set_name}${xlen} Extension){{$}}

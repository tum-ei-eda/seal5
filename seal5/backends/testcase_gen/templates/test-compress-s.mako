// SPDX-License-Identifier: Apache-2.0
//
// This file is part of the M2-ISA-R project: https://github.com/tum-ei-eda/M2-ISA-R
//
// Copyright (c) 2025 TUM Department of Electrical and Computer Engineering.
// Copyright (c) 2025 DLR - Institute of Systems Engineering for Future Mobility

// Generated on ${start_time}.
//
// This file contains the Info for generating invalid tests for the ${set_name} 
// core architecture.



// RUN: llvm-mc -triple riscv${xlen} -mattr=+${arch} -show-encoding \
// RUN:   -riscv-no-aliases < %s | FileCheck -check-prefixes=CHECK,CHECK-INST %s

// CHECK-INST: ${mnemonic} s0, 14
// CHECK: # encoding: [0x38,0x88]
${mnemonic} s0, s0, 14

// TODO: add commutativity pattern
// ${mnemonic} s0, 14, s0

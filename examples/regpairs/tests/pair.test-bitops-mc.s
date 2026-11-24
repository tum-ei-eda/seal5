# RUN: llvm-mc -triple=riscv32 -mattr=+xregpairs -show-encoding %s | FileCheck %s
# RUN: llvm-mc -triple=riscv32 -mattr=+xregpairs -filetype=obj %s -o %t.o
# RUN: llvm-objdump -d --no-print-imm-hex --mattr=+xregpairs --disassembler-options=numeric %t.o | FileCheck %s --check-prefix=DIS
pair.xor64 x10, x12, x14
# CHECK: pair.xor64 a0, a2, a4 # encoding: [0x0b,0x55,0xe6,0x00]
# DIS: pair.xor64 x10, x12, x14
pair.and64 x10, x12, x14
# CHECK: pair.and64 a0, a2, a4 # encoding: [0x0b,0x65,0xe6,0x00]
# DIS: pair.and64 x10, x12, x14
pair.slli64 x10, x12, 0
# CHECK: pair.slli64 a0, a2, 0 # encoding: [0x0b,0x75,0x06,0x00]
# DIS: pair.slli64 x10, x12, 0
pair.srli64 x10, x12, 32
# CHECK: pair.srli64 a0, a2, 32 # encoding: [0x0b,0x75,0x06,0x06]
# DIS: pair.srli64 x10, x12, 32
pair.srai64 x10, x12, 63
# CHECK: pair.srai64 a0, a2, 63 # encoding: [0x0b,0x75,0xf6,0x0b]
# DIS: pair.srai64 x10, x12, 63
pair.rori64 x10, x12, 33
# CHECK: pair.rori64 a0, a2, 33 # encoding: [0x0b,0x75,0x16,0x0e]
# DIS: pair.rori64 x10, x12, 33

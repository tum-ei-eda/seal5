# RUN: llvm-mc -triple=riscv32 -mattr=+xregpairs -show-encoding %s | FileCheck %s
# RUN: llvm-mc -triple=riscv32 -mattr=+xregpairs -filetype=obj %s -o %t.o
# RUN: llvm-objdump -d --mattr=+xregpairs --disassembler-options=numeric %t.o | FileCheck %s --check-prefix=DIS
# RUN: not llvm-mc -triple=riscv32 %s 2>&1 | FileCheck %s --check-prefix=OFF
# RUN: not llvm-mc -triple=riscv64 -mattr=+xregpairs %s 2>&1 | FileCheck %s --check-prefix=RV64
pair.add64 x10, x12, x14
# CHECK: pair.add64 a0, a2, a4 # encoding: [0x0b,0x05,0xe6,0x00]
# DIS: pair.add64 x10, x12, x14
pair.add.2x32 x30, x0, x2
# CHECK: pair.add.2x32 t5, zero, sp # encoding: [0x0b,0x1f,0x20,0x00]
# DIS: pair.add.2x32 x30, x0, x2
pair.add64 x0, x30, x30
# CHECK: pair.add64 zero, t5, t5 # encoding: [0x0b,0x00,0xef,0x01]
# OFF: error: instruction requires the following:
# RV64: error: invalid operand for instruction

pair.sub64 x10, x12, x14
# CHECK: pair.sub64 a0, a2, a4 # encoding: [0x0b,0x25,0xe6,0x00]
# DIS: pair.sub64 x10, x12, x14

pair.sub.2x32 x10, x12, x14
# CHECK: pair.sub.2x32 a0, a2, a4 # encoding: [0x0b,0x35,0xe6,0x00]
# DIS: pair.sub.2x32 x10, x12, x14

pair.mul.2x32 x10, x12, x14
# CHECK: pair.mul.2x32 a0, a2, a4 # encoding: [0x0b,0x45,0xe6,0x00]
# DIS: pair.mul.2x32 x10, x12, x14

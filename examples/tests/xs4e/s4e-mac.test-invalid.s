# MC test of sample S4E MAC instruction extensions

# RUN: not llvm-mc -triple=riscv32 --mattr=+xs4emac %s 2>&1 \
# RUN:        | FileCheck %s --check-prefixes=CHECK-ERROR

s4e.reset_acc 0
# CHECK-ERROR: invalid operand for instruction

s4e.reset_acc t1
# CHECK-ERROR: invalid operand for instruction

s4e.get_acc_lo 0
# CHECK-ERROR: invalid operand for instruction

s4e.get_acc_hi 0
# CHECK-ERROR: invalid operand for instruction

s4e.macu_32 s5, 0
# CHECK-ERROR: invalid operand for instruction

s4e.macs_32 0, a7
# CHECK-ERROR: invalid operand for instruction

s4e.macu_64 s5, 0
# CHECK-ERROR: invalid operand for instruction

s4e.macs_64 0, a7
# CHECK-ERROR: invalid operand for instruction

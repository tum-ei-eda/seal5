# RUN: not llvm-mc -triple=riscv32 --mattr=+xrvc %s 2>&1 \
# RUN:        | FileCheck %s --check-prefixes=CHECK-ERROR

xrv.nandi a0, a1, 5555 # CHECK-ERROR: operand must be a symbol with %lo/%pcrel_lo/%tprel_lo modifier or an integer in the range [-2048, 2047]

xrv.nandi a0, a1, a2 # CHECK-ERROR: operand must be a symbol with %lo/%pcrel_lo/%tprel_lo modifier or an integer in the range [-2048, 2047]

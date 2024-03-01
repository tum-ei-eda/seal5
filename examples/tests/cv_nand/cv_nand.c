// RUN: clang -cc1 -triple riscv32 -target-feature +m -target-feature +xcvnand -S -O3 %s -o - \
// RUN:     | FileCheck %s  -check-prefix=CHECK

// CHECK-LABEL: nand_bitwise_s32:
// CHECK-COUNT-1: cv.nand_bitwise {{.*}}
signed int nand_bitwise_s32(signed int a, signed int b)
{
  return ~(a & b);
}

// CHECK-LABEL: nand_bitwise_u32:
// CHECK-COUNT-1: cv.nand_bitwise {{.*}}
unsigned int nand_bitwise_u32(unsigned int a, unsigned int b)
{
  return ~(a & b);
}

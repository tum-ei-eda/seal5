// RUN: %clang --target=riscv32 -march=rv32ixs4emac -c -o %t.o %s
// RUN: llvm-objdump --disassembler-options=numeric -d %t.o | FileCheck %s

int main() {
  // CHECK: 0b 90 1a 01 cv.abs x1, x2
  asm("cv.abs x1, x2");

  return 0;
}

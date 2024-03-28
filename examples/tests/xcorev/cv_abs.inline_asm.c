// RUN: %clang --target=riscv32 -march=rv32ixcorevalu -c -o %t.o %s
// RUN: llvm-objdump --disassembler-options=numeric -d %t.o | FileCheck %s

int main() {
  // CHECK: 0b 90 1a 01 seal5.cv.abs x1, x2
  asm("seal5.cv.abs x1, x2");

  return 0;
}

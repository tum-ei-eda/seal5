// RUN: %clang --target=riscv32 -march=rv32xcorevmac -c -o %t.o %s
// RUN: llvm-objdump --disassembler-options=numeric -d %t.o | FileCheck %s

int main() {
  // CHECK: 0b 90 1a 01 seal5.cv.mac x1, x2, x3
  asm("seal5.cv.mac x1, x2, x3");

  return 0;
}

// RUN: clang --target=riscv32 -march=rv32ixchacha -c -o %t.o %s
// RUN: llvm-objdump --disassembler-options=numeric -d %t.o | FileCheck %s

int main() {
  // CHECK: 0052018b chacha.xorrol16 x3, x4, x5
  asm("chacha.xorrol16 x3, x4, x5");

  return 42;
}

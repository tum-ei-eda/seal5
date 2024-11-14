// RUN: clang --target=riscv32 -march=rv32ixs4emac -c -o %t.o %s
// RUN: llvm-objdump --disassembler-options=numeric -d %t.o | FileCheck %s

int main() {
  // CHECK: 0b 00 00 00 s4e.reset_acc
  asm("s4e.reset_acc");

  return 42;
}

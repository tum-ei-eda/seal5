// RUN: clang --target=riscv32 -march=rv32ixs4emac -c -o %t.o %s
// RUN: llvm-objdump --disassembler-options=numeric -d %t.o | FileCheck %s

int main() {
  // CHECK: 8b 0c 00 04 s4e.get_acc_hi x25
  asm("s4e.get_acc_hi x25");

  return 42;
}

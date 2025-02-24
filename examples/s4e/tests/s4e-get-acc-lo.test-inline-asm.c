// RUN: clang --target=riscv32 -march=rv32ixs4emac -c -o %t.o %s
// RUN: llvm-objdump --disassembler-options=numeric -d %t.o | FileCheck %s

int main() {
  // CHECK: 0b 03 00 02 s4e.get_acc_lo x6
  asm("s4e.get_acc_lo x6");

  return 42;
}

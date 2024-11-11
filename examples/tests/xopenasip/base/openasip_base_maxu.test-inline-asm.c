// RUN: clang -c -target riscv32-unknown-elf -march=rv32i -Xclang -target-feature -Xclang +xopenasipbase -O3 -o %t.o %s
// RUN: llvm-objdump --mattr=+i,+xopenasipbase --disassembler-options=numeric -d %t.o | FileCheck %s

__attribute__((naked)) void test_max_asm() {
    // CHECK: 8b 8a b5 2b openasip_base_max x21, x11, x27
    asm("openasip_base_max x21, x11, x27");
}

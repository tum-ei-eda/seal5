// RUN: clang -c -target riscv32-unknown-elf -march=rv32i -Xclang -target-feature -Xclang +experimental-xopenasipbase -O3 -o %t.o %s
// RUN: llvm-objdump --mattr=+i,+experimental-xopenasipbase --disassembler-options=numeric -d %t.o | FileCheck %s

__attribute__((naked)) void test_max_asm() {
    // CHECK: 2bb58a8b openasip_base_max x21, x11, x27
    asm("openasip_base_max x21, x11, x27");
}

// RUN: clang -c -target riscv32-unknown-elf -march=rv32ic -Xclang -target-feature -Xclang +xrvc -mllvm -global-isel=1 -O3 -o %t.o %s
// RUN: llvm-objdump --mattr=+i,+xrvc --disassembler-options=numeric -d %t.o | FileCheck %s

int test_nand(int a, int b) {
    // CHECK: 2b 65 b5 92 xrv.nand x10, x10, x11
    return ~(a & b);
}

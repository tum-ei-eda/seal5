// RUN: clang -c -target riscv32-unknown-elf -march=rv32ic -Xclang -target-feature -Xclang +xrvc -mllvm -global-isel=1 -O3 -o %t.o %s
// RUN: llvm-objdump --mattr=+i,+xrvc --disassembler-options=numeric -d %t.o | FileCheck %s

int test_nandi(int a) {
    // CHECK: 0b 05 b5 2a xrvc.nand x10, 31
    return ~(a & 31);
}

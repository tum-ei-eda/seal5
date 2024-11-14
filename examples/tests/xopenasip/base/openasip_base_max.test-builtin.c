// RUN: clang -c -target riscv32-unknown-elf -march=rv32ixopenasipbase1p0 -menable-experimental-extensions -o %t.o %s
// RUN: llvm-objdump --disassembler-options=numeric -d %t.o | FileCheck %s

int test_intrinsic(int a, int b) {
    // CHECK: <test_intrinsic>
    // CHECK: openasip_base_max
    return __builtin_xopenasipbase_openasip_base_max(a, b);
}

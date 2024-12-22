// RUN: clang -c -target riscv32-unknown-elf -march=rv32ixexample -o %t.o %s
// RUN: llvm-objdump --disassembler-options=numeric -d %t.o | FileCheck %s


int test_intrinsic(int a, int b, int c) {
    // CHECK: <test_intrinsic>
    // Can't rely upon specific registers being used but at least instruction should have been used
    // CHECK: xexample.subincacc
    c = __builtin_riscv_xexample_subincacc(a, b, c);
}

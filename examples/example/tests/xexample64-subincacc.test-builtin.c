// RUN: clang -c -target riscv64-unknown-elf -march=rv64ixexample -o %t.o %s
// RUN: llvm-objdump --disassembler-options=numeric -d %t.o | FileCheck %s


int test_intrinsic(int a, int b, int c) {
    // CHECK: <test_intrinsic>
    // Can't rely upon specific registers being used but at least instruction should have been used
    // CHECK: xexample64.subincacc
    c = __builtin_riscv_xexample_subincacc(a, b, c);
}

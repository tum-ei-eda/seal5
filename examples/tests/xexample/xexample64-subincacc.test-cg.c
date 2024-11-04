// RUN: clang -c -target riscv64-unknown-elf -march=rv64i -Xclang -target-feature -Xclang +xexample -mllvm -global-isel=1 -O3 -o %t.o %s
// RUN: llvm-objdump --mattr=+i,+xexample --disassembler-options=numeric -d %t.o | FileCheck %s

long test_subincacc(long a, long b, long c) {
    // CHECK: 2b 36 b5 50 xexample64.subincacc x12, x10, x11
    return ((a + 1) - b) + c;
}

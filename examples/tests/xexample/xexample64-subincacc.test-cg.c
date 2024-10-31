// RUN: clang -c -target riscv64unknown-elf -march=rv64i -Xclang -target-feature -Xclang +xexample64 -mllvm -global-isel=1 -O3 -o %t.o %s
// RUN: llvm-objdump --mattr=+i,+xexample64 --disassembler-options=numeric -d %t.o | FileCheck %s

long test_subincacc(long a, long b, long c) {
    // CHECK: 0b 05 b5 2a xexample64.subincacc x10, x10, x11
    return a + (b - c + 1);
}

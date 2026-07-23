// RUN: clang -O3 -target riscv32-unknown-elf -Xclang -target-feature -Xclang +xchacha -o - %s -c | llvm-objdump - -d | FileCheck --check-prefixes=CHECK-OBJ %s
// RUN: clang -O3 -target riscv32-unknown-elf -Xclang -target-feature -Xclang +xchacha -o - %s -S -emit-llvm | FileCheck --check-prefixes=CHECK-LL %s

int __builtin_xchacha_xorrol16(int, int);

int test_xorrol16(int a, int b) {
    // CHECK-OBJ: <test_xorrol16>
    // CHECK-OBJ-NEXT: chacha.xorrol16
    // CHECK-LL-LABEL: @test_xorrol16
    // CHECK-LL-NEXT:    [[TMP0:%.*]] = tail call i32 @llvm.riscv.xchacha.xorrol16(i32 %0, i32 %1)
    // CHECK-LL-NEXT:    ret i32 [[TMP0]]
    return __builtin_riscv_xchacha_xorrol16(a, b);
}

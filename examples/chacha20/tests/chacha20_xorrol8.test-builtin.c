// RUN: clang -O3 -target riscv32-unknown-elf -Xclang -target-feature -Xclang +xchacha -o - %s -c | llvm-objdump - -d | FileCheck --check-prefixes=CHECK-OBJ %s
// RUN: clang -O3 -target riscv32-unknown-elf -Xclang -target-feature -Xclang +xchacha -o - %s -S -emit-llvm | FileCheck --check-prefixes=CHECK-LL %s

int __builtin_xchacha_xorrol8(int, int);

int test_xorrol8(int a, int b) {
    // CHECK-OBJ: <test_xorrol8>
    // CHECK-OBJ-NEXT: chacha.xorrol8
    // CHECK-LL-LABEL: @test_xorrol8
    // CHECK-LL-NEXT:    [[TMP0:%.*]] = tail call i32 @llvm.riscv.xchacha.xorrol8(i32 %0, i32 %1)
    // CHECK-LL-NEXT:    ret i32 [[TMP0]]
    return __builtin_riscv_xchacha_xorrol8(a, b);
}

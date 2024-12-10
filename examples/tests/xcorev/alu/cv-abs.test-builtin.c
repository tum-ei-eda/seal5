// RUN: clang -target riscv32-unknown-elf -Xclang -target-feature -Xclang +xcorevalu -o - %s -c | llvm-objdump - -d | FileCheck --check-prefixes=CHECK-OBJ %s
// RUN: clang -target riscv32-unknown-elf -Xclang -target-feature -Xclang +xcorevalu -o - %s -S -emit-llvm | FileCheck --check-prefixes=CHECK-LL %s

int test_abs(int a) {
    // CHECK-OBJ: <test_intrinsic>
    // CHECK-OBJ-NEXT: cv.abs
    // CHECK-LL-LABEL: @test_intrinsic
    // CHECK-LL-NEXT:  entry:
    // CHECK-LL-NEXT:    [[A_ADDR:%.*]] = alloca i32, align 4
    // CHECK-LL-NEXT:    store i32 [[A:%.*]], ptr [[A_ADDR]], align 4
    // CHECK-LL-NEXT:    [[TMP0:%.*]] = load i32, ptr [[A_ADDR]], align 4
    // CHECK-LL-NEXT:    [[TMP1:%.*]] = call i32 @llvm.riscv.xcorev.alu.abs(i32 [[TMP0]])
    return __builtin_riscv_xcorev_alu_abs(a);
}

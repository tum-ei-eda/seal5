// RUN: clang -target riscv32-unknown-elf -Xclang -target-feature -Xclang +xcorevmac -o - %s -c | llvm-objdump - -d | FileCheck --check-prefixes=CHECK-OBJ %s
// RUN: clang -target riscv32-unknown-elf -Xclang -target-feature -Xclang +xcorevmac -o - %s -S -emit-llvm | FileCheck --check-prefixes=CHECK-LL %s

int test_mac(int a) {
    // CHECK-OBJ: <test_mac>
    // CHECK-OBJ-NEXT: cv.mac
    // CHECK-LL-LABEL: @test_mac
    // CHECK-LL-NEXT:  entry:
    // CHECK-LL-NEXT:    [[A_ADDR:%.*]] = alloca i32, align 4
    // CHECK-LL-NEXT:    store i32 [[A:%.*]], ptr [[A_ADDR]], align 4
    // CHECK-LL-NEXT:    [[TMP0:%.*]] = load i32, ptr [[A_ADDR]], align 4
    // CHECK-LL-NEXT:    [[TMP1:%.*]] = call i32 @llvm.riscv.xcorev.mac.mac(i32 [[TMP0]])
    return __builtin_riscv_xcorev_mac_mac(a);
}

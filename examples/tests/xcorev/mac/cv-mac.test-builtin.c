// RUN: clang -O3 -target riscv32-unknown-elf -Xclang -target-feature -Xclang +xcorevmac -o - %s -c | llvm-objdump - -d | FileCheck --check-prefixes=CHECK-OBJ %s
// RUN: clang -O3 -target riscv32-unknown-elf -Xclang -target-feature -Xclang +xcorevmac -o - %s -S -emit-llvm | FileCheck --check-prefixes=CHECK-LL %s

int __builtin_xcorevmac_mac_mac(int, int, int);

int test_mac(int a, int b, int c) {
    // CHECK-OBJ: <test_mac>
    // CHECK-OBJ-NEXT: seal5.cv.mac
    // CHECK-LL-LABEL: @test_mac
    // CHECK-LL-NEXT:  entry:
    // CHECK-LL-NEXT:    [[TMP0:%.*]] = tail call i32 @llvm.riscv.xcorevmac.mac.mac(i32 %a, i32 %b, i32 %c)
    // CHECK-LL-NEXT:    ret i32 [[TMP0]]
    return __builtin_riscv_xcorevmac_mac_mac(a, b, c);
}

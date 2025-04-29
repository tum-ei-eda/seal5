// RUN: clang -O3 -target riscv32-unknown-elf -Xclang -target-feature -Xclang +xcorevalu -o - %s -c | llvm-objdump - -d | FileCheck --check-prefixes=CHECK-OBJ %s
// RUN: clang -O3 -target riscv32-unknown-elf -Xclang -target-feature -Xclang +xcorevalu -o - %s -S -emit-llvm | FileCheck --check-prefixes=CHECK-LL %s

int __builtin_riscv_xcorevalu_alu_abs(int);

int test_abs(int a) {
    // CHECK-OBJ: <test_abs>
    // CHECK-OBJ-NEXT: seal5.cv.abs
    // CHECK-LL-LABEL: @test_abs
    // CHECK-LL-NEXT:  entry:
    // CHECK-LL-NEXT:    [[TMP0:%.*]] = tail call i32 @llvm.riscv.xcorevalu.alu.abs(i32 %a)
    // CHECK-LL-NEXT:    ret i32 [[TMP0]]
    return __builtin_riscv_xcorevalu_alu_abs(a);
}

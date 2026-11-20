// RUN: clang --target=riscv32 -march=rv32imxregpairs -O0 -S %s -o - | FileCheck %s
// RUN: clang --target=riscv32 -march=rv32imxregpairs -O3 -S %s -o - | FileCheck %s
// RUN: clang --target=riscv32 -march=rv32imxregpairs -O3 -S -emit-llvm %s -o - | FileCheck %s --check-prefix=IR
// RUN: not clang --target=riscv32 -march=rv32im -O2 -S %s -o /dev/null 2>&1 | FileCheck %s --check-prefix=OFF
#include <stdint.h>
uint64_t add64(uint64_t a, uint64_t b) {
  // CHECK-LABEL: add64:
  // CHECK: pair.add64
  // IR: call i64 @llvm.riscv.xregpairs.add64
  return __builtin_riscv_xregpairs_add64(a, b);
}
uint64_t add_2x32(uint64_t a, uint64_t b) {
  // CHECK-LABEL: add_2x32:
  // CHECK: pair.add.2x32
  // IR: call i64 @llvm.riscv.xregpairs.add.2x32
  return __builtin_riscv_xregpairs_add_2x32(a, b);
}
// OFF: needs target feature xregpairs
uint64_t add_zero(uint64_t a) {
  // CHECK-LABEL: add_zero:
  // CHECK: pair.add64
  // IR: call i64 @llvm.riscv.xregpairs.add64
  return __builtin_riscv_xregpairs_add64(a, 0);
}

uint64_t sub64(uint64_t a, uint64_t b) {
  // CHECK-LABEL: sub64:
  // CHECK: pair.sub64
  // IR: call i64 @llvm.riscv.xregpairs.sub64
  return __builtin_riscv_xregpairs_sub64(a, b);
}

uint64_t sub_2x32(uint64_t a, uint64_t b) {
  // CHECK-LABEL: sub_2x32:
  // CHECK: pair.sub.2x32
  // IR: call i64 @llvm.riscv.xregpairs.sub.2x32
  return __builtin_riscv_xregpairs_sub_2x32(a, b);
}

uint64_t mul_2x32(uint64_t a, uint64_t b) {
  // CHECK-LABEL: mul_2x32:
  // CHECK: pair.mul.2x32
  // IR: call i64 @llvm.riscv.xregpairs.mul.2x32
  return __builtin_riscv_xregpairs_mul_2x32(a, b);
}

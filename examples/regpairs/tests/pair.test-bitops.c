// RUN: clang --target=riscv32 -march=rv32imxregpairs -O0 -S %s -o - | FileCheck %s
// RUN: clang --target=riscv32 -march=rv32imxregpairs -O3 -S %s -o - | FileCheck %s
// SPDX-License-Identifier: Apache-2.0
#include <stdint.h>
uint64_t bit_xor64(uint64_t a, uint64_t b) {
  // CHECK-LABEL: bit_xor64:
  // CHECK: pair.xor64
  return __builtin_riscv_xregpairs_xor64(a,b);
}
uint64_t auto_xor64(uint64_t a, uint64_t b) { return a ^ b; }
uint64_t bit_and64(uint64_t a, uint64_t b) {
  // CHECK-LABEL: bit_and64:
  // CHECK: pair.and64
  return __builtin_riscv_xregpairs_and64(a,b);
}
uint64_t auto_and64(uint64_t a, uint64_t b) { return a & b; }
uint64_t bit_slli64(uint64_t a, unsigned count) {
  // CHECK-LABEL: bit_slli64:
  // CHECK: pair.slli64
  switch (count) {
  case 0: return __builtin_riscv_xregpairs_slli64(a,0);
  case 1: return __builtin_riscv_xregpairs_slli64(a,1);
  case 31: return __builtin_riscv_xregpairs_slli64(a,31);
  case 32: return __builtin_riscv_xregpairs_slli64(a,32);
  case 33: return __builtin_riscv_xregpairs_slli64(a,33);
  case 63: return __builtin_riscv_xregpairs_slli64(a,63);
  default: return 0;
  }
}
uint64_t auto_slli64(uint64_t a, unsigned count) {
  switch (count) {
  case 0: return a << 0;
  case 1: return a << 1;
  case 31: return a << 31;
  case 32: return a << 32;
  case 33: return a << 33;
  case 63: return a << 63;
  default: return 0;
  }
}
uint64_t bit_srli64(uint64_t a, unsigned count) {
  // CHECK-LABEL: bit_srli64:
  // CHECK: pair.srli64
  switch (count) {
  case 0: return __builtin_riscv_xregpairs_srli64(a,0);
  case 1: return __builtin_riscv_xregpairs_srli64(a,1);
  case 31: return __builtin_riscv_xregpairs_srli64(a,31);
  case 32: return __builtin_riscv_xregpairs_srli64(a,32);
  case 33: return __builtin_riscv_xregpairs_srli64(a,33);
  case 63: return __builtin_riscv_xregpairs_srli64(a,63);
  default: return 0;
  }
}
uint64_t auto_srli64(uint64_t a, unsigned count) {
  switch (count) {
  case 0: return a >> 0;
  case 1: return a >> 1;
  case 31: return a >> 31;
  case 32: return a >> 32;
  case 33: return a >> 33;
  case 63: return a >> 63;
  default: return 0;
  }
}
uint64_t bit_srai64(uint64_t a, unsigned count) {
  // CHECK-LABEL: bit_srai64:
  // CHECK: pair.srai64
  switch (count) {
  case 0: return __builtin_riscv_xregpairs_srai64(a,0);
  case 1: return __builtin_riscv_xregpairs_srai64(a,1);
  case 31: return __builtin_riscv_xregpairs_srai64(a,31);
  case 32: return __builtin_riscv_xregpairs_srai64(a,32);
  case 33: return __builtin_riscv_xregpairs_srai64(a,33);
  case 63: return __builtin_riscv_xregpairs_srai64(a,63);
  default: return 0;
  }
}
uint64_t auto_srai64(uint64_t a, unsigned count) {
  switch (count) {
  case 0: return (uint64_t)((int64_t)a >> 0);
  case 1: return (uint64_t)((int64_t)a >> 1);
  case 31: return (uint64_t)((int64_t)a >> 31);
  case 32: return (uint64_t)((int64_t)a >> 32);
  case 33: return (uint64_t)((int64_t)a >> 33);
  case 63: return (uint64_t)((int64_t)a >> 63);
  default: return 0;
  }
}
uint64_t bit_rori64(uint64_t a, unsigned count) {
  // CHECK-LABEL: bit_rori64:
  // CHECK: pair.rori64
  switch (count) {
  case 0: return __builtin_riscv_xregpairs_rori64(a,0);
  case 1: return __builtin_riscv_xregpairs_rori64(a,1);
  case 31: return __builtin_riscv_xregpairs_rori64(a,31);
  case 32: return __builtin_riscv_xregpairs_rori64(a,32);
  case 33: return __builtin_riscv_xregpairs_rori64(a,33);
  case 63: return __builtin_riscv_xregpairs_rori64(a,63);
  default: return 0;
  }
}
uint64_t auto_rori64(uint64_t a, unsigned count) {
  switch (count) {
  case 0: return __builtin_rotateright64(a, 0);
  case 1: return __builtin_rotateright64(a, 1);
  case 31: return __builtin_rotateright64(a, 31);
  case 32: return __builtin_rotateright64(a, 32);
  case 33: return __builtin_rotateright64(a, 33);
  case 63: return __builtin_rotateright64(a, 63);
  default: return 0;
  }
}

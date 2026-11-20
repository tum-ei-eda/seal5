// SPDX-License-Identifier: Apache-2.0
#include <stdint.h>
typedef uint32_t lanes2 __attribute__((vector_size(8)));
uint64_t automatic_add64(uint64_t a, uint64_t b) { return a + b; }
uint64_t automatic_add_2x32(uint64_t a, uint64_t b) {
  lanes2 x, y, z;
  __builtin_memcpy(&x, &a, 8);
  __builtin_memcpy(&y, &b, 8);
  z = x + y;
  uint64_t result;
  __builtin_memcpy(&result, &z, 8);
  return result;
}
uint64_t automatic_sub64(uint64_t a, uint64_t b) { return a - b; }
uint64_t automatic_sub_2x32(uint64_t a, uint64_t b) {
  lanes2 x, y, z;
  __builtin_memcpy(&x, &a, 8);
  __builtin_memcpy(&y, &b, 8);
  z = x - y;
  uint64_t result;
  __builtin_memcpy(&result, &z, 8);
  return result;
}
uint64_t automatic_mul_2x32(uint64_t a, uint64_t b) {
  lanes2 x, y, z;
  __builtin_memcpy(&x, &a, 8);
  __builtin_memcpy(&y, &b, 8);
  z = x * y;
  uint64_t result;
  __builtin_memcpy(&result, &z, 8);
  return result;
}

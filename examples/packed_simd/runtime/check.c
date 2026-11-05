// SPDX-License-Identifier: Apache-2.0
#include <stdint.h>
static uint32_t ref(uint32_t a, uint32_t b, unsigned bits, unsigned sub) {
  uint32_t result = 0, mask = (1u << bits) - 1;
  for (unsigned i = 0; i < 32; i += bits) {
    uint32_t x = (a >> i) & mask, y = (b >> i) & mask;
    result |= ((sub ? x - y : x + y) & mask) << i;
  }
  return result;
}
#define OP(F, S, A, B, R)                                                      \
  __asm__ volatile(".insn r 0x2b, " #F ", " #S ", %0, %1, %2"                  \
                   : "=r"(R)                                                   \
                   : "r"(A), "r"(B))
int benchmark(void) {
  uint32_t a = 0xffffffffu, b = 1;
  for (unsigned i = 0; i < 1024; ++i) {
    uint32_t r;
    OP(0, 0, a, b, r);
    if (r != ref(a, b, 8, 0))
      return 1;
    OP(1, 0, a, b, r);
    if (r != ref(a, b, 16, 0))
      return 2;
    OP(0, 1, a, b, r);
    if (r != ref(a, b, 8, 1))
      return 3;
    OP(1, 1, a, b, r);
    if (r != ref(a, b, 16, 1))
      return 4;
    r = a;
    __asm__ volatile(".insn r 0x2b, 0, 0, %0, %0, %1" : "+r"(r) : "r"(b));
    if (r != ref(a, b, 8, 0))
      return 5;
    __asm__ volatile(".insn r 0x2b, 0, 0, x0, %1, %2\nadd %0, x0, x0"
                     : "=r"(r)
                     : "r"(a), "r"(b));
    if (r)
      return 6;
    a ^= a << 13;
    a ^= a >> 17;
    a ^= a << 5;
    b = b * 1664525u + 1013904223u;
  }
  return 0;
}
int verify_benchmark(int result) { return result == 0; }
void initialise_benchmark(void) {}
void warm_caches(int n) {
  while (n-- > 0)
    benchmark();
}

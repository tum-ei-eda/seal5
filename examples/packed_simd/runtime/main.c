// SPDX-License-Identifier: Apache-2.0
#include "support.h"
#include <stdint.h>

static uint32_t instructions(void) {
  uint32_t value;
  __asm__ volatile("rdinstret %0" : "=r"(value)::"memory");
  return value;
}
static uint32_t cycles(void) {
  uint32_t value;
  __asm__ volatile("rdcycle %0" : "=r"(value)::"memory");
  return value;
}
int seal5_main(void) {
  initialise_benchmark();
  warm_caches(1);
  __asm__ volatile(".insn r 0x2b, 7, 0, x0, x0, x0" ::: "memory");
  uint32_t i0 = instructions(), c0 = cycles();
  int result = benchmark();
  uint32_t c1 = cycles(), i1 = instructions();
  uint32_t di = i1 - i0, dc = c1 - c0;
  __asm__ volatile(".insn r 0x2b, 7, 1, x0, %0, %1" ::"r"(di), "r"(dc)
                   : "memory");
  return verify_benchmark(result) == 1 ? 0 : 1;
}

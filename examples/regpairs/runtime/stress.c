// SPDX-License-Identifier: Apache-2.0
#include <stdint.h>
extern void opaque(void);
uint64_t stress(const uint64_t *a, const uint64_t *b) {
#define PAIR(N) uint64_t t##N = __builtin_riscv_xregpairs_add64(a[N], b[N])
  PAIR(0); PAIR(1); PAIR(2); PAIR(3); PAIR(4); PAIR(5);
  PAIR(6); PAIR(7); PAIR(8); PAIR(9); PAIR(10); PAIR(11);
  opaque();
  return t0 + t1 + t2 + t3 + t4 + t5 + t6 + t7 + t8 + t9 + t10 + t11;
}

// SPDX-License-Identifier: Apache-2.0
// Compile this independent reference with a baseline RV32 GCC.
#include <stdint.h>
extern uint64_t automatic_add64(uint64_t, uint64_t);
extern uint64_t automatic_add_2x32(uint64_t, uint64_t);
extern uint64_t sub64(uint64_t, uint64_t);
extern uint64_t ir_sub64(uint64_t, uint64_t);
extern uint64_t automatic_sub64(uint64_t, uint64_t);
extern uint64_t sub_2x32(uint64_t, uint64_t);
extern uint64_t ir_sub_2x32(uint64_t, uint64_t);
extern uint64_t automatic_sub_2x32(uint64_t, uint64_t);
extern uint64_t mul_2x32(uint64_t, uint64_t);
extern uint64_t ir_mul_2x32(uint64_t, uint64_t);
extern uint64_t automatic_mul_2x32(uint64_t, uint64_t);
extern uint64_t add64(uint64_t, uint64_t);
extern uint64_t add_zero(uint64_t);
extern uint64_t add_2x32(uint64_t, uint64_t);
extern uint64_t ir_add64(uint64_t, uint64_t);
extern uint64_t ir_add_2x32(uint64_t, uint64_t);
extern uint64_t unaligned_abi(uint32_t, uint64_t, uint64_t);
extern uint64_t stress(const uint64_t *, const uint64_t *);
extern int pair_alias_test(void);
extern int pair_bit_checks(uint64_t,uint64_t);
void opaque(void) { __asm__ volatile ("" ::: "memory"); }
static uint32_t state = 0x12345678;
static uint32_t next(void) {
  state ^= state << 13; state ^= state >> 17; state ^= state << 5;
  return state;
}
static uint64_t wide(void) { return ((uint64_t)next() << 32) | next(); }
static uint64_t packed(uint64_t a, uint64_t b) {
  uint32_t lo = (uint32_t)a + (uint32_t)b;
  uint32_t hi = (uint32_t)(a >> 32) + (uint32_t)(b >> 32);
  return ((uint64_t)hi << 32) | lo;
}
static uint64_t packed_sub(uint64_t a, uint64_t b) {
  return (uint32_t)((uint32_t)a - (uint32_t)b) |
    ((uint64_t)(uint32_t)((uint32_t)(a >> 32) - (uint32_t)(b >> 32)) << 32);
}
static uint64_t packed_mul(uint64_t a, uint64_t b) {
  return (uint32_t)((uint32_t)a * (uint32_t)b) |
    ((uint64_t)(uint32_t)((uint32_t)(a >> 32) * (uint32_t)(b >> 32)) << 32);
}
static int extra_checks(uint64_t a, uint64_t b) {
  return pair_bit_checks(a,b) || sub64(a, b) != a - b || ir_sub64(a, b) != a - b ||
    automatic_sub64(a, b) != a - b ||
    sub_2x32(a, b) != packed_sub(a, b) || ir_sub_2x32(a, b) != packed_sub(a, b) ||
    automatic_sub_2x32(a, b) != packed_sub(a, b) ||
    mul_2x32(a, b) != packed_mul(a, b) || ir_mul_2x32(a, b) != packed_mul(a, b) ||
    automatic_mul_2x32(a, b) != packed_mul(a, b);
}
int seal5_main(void) {
  static const uint64_t edge[] = {0, 1, 0xffffffff, 0x100000000,
    0x7fffffffffffffff, 0x8000000000000000, 0xffffffffffffffff};
  if (pair_alias_test()) return 1;
  for (unsigned i = 0; i < 7; ++i)
    for (unsigned j = 0; j < 7; ++j)
      if (extra_checks(edge[i], edge[j]) || add64(edge[i], edge[j]) != edge[i] + edge[j] ||
          add_2x32(edge[i], edge[j]) != packed(edge[i], edge[j])) return 2;
  for (unsigned i = 0; i < 4096; ++i) {
    uint64_t a = wide(), b = wide(); uint32_t prefix = next();
    if (extra_checks(a, b) || automatic_add64(a, b) != a + b || automatic_add_2x32(a, b) != packed(a, b) ||
        add_zero(a) != a || add64(a, b) != a + b || add_2x32(a, b) != packed(a, b) ||
        ir_add64(a, b) != a + b || ir_add_2x32(a, b) != packed(a, b) ||
        unaligned_abi(prefix, a, b) != a + b + prefix) return 3;
  }
  for (unsigned n = 0; n < 128; ++n) {
    uint64_t a[12], b[12], sum = 0;
    for (unsigned i = 0; i < 12; ++i) { a[i] = wide(); b[i] = wide(); sum += a[i] + b[i]; }
    if (stress(a, b) != sum) return 4;
  }
  return 0;
}

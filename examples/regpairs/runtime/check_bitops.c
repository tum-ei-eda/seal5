// SPDX-License-Identifier: Apache-2.0
#include <stdint.h>
extern uint64_t bit_xor64(uint64_t, uint64_t);
extern uint64_t bit_and64(uint64_t, uint64_t);
extern uint64_t bit_slli64(uint64_t, unsigned);
extern uint64_t bit_srli64(uint64_t, unsigned);
extern uint64_t bit_srai64(uint64_t, unsigned);
extern uint64_t bit_rori64(uint64_t, unsigned);
extern uint64_t auto_xor64(uint64_t, uint64_t);
extern uint64_t auto_and64(uint64_t, uint64_t);
extern uint64_t auto_slli64(uint64_t, unsigned);
extern uint64_t auto_srli64(uint64_t, unsigned);
extern uint64_t auto_srai64(uint64_t, unsigned);
extern uint64_t auto_rori64(uint64_t, unsigned);
int pair_bit_checks(uint64_t a, uint64_t b) {
  if (bit_xor64(a, b) != (a ^ b) || auto_xor64(a, b) != (a ^ b) ||
      bit_and64(a, b) != (a & b) || auto_and64(a, b) != (a & b))
    return 1;
  static const unsigned counts[] = {0, 1, 31, 32, 33, 63};
  for (unsigned i = 0; i < 6; i++) {
    unsigned n = counts[i];
    uint64_t r = n ? (a >> n) | (a << (64 - n)) : a;
    if (bit_slli64(a, n) != (a << n))
      return 2;
    if (bit_srli64(a, n) != (a >> n))
      return 2;
    if (bit_srai64(a, n) != ((uint64_t)((int64_t)a >> n)))
      return 2;
    if (bit_rori64(a, n) != (r))
      return 2;
    if (auto_slli64(a, n) != (a << n))
      return 2;
    if (auto_srli64(a, n) != (a >> n))
      return 2;
    if (auto_srai64(a, n) != ((uint64_t)((int64_t)a >> n)))
      return 2;
    if (auto_rori64(a, n) != (r))
      return 2;
  }
  return 0;
}

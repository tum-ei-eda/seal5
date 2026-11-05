// SPDX-License-Identifier: Apache-2.0
// Independent scalar references for the hand-written LLVM IR regressions.
#include <stdint.h>
extern void dsp(const int16_t *, const int16_t *, int16_t *);
extern void narrow(const uint8_t *, uint8_t *);
extern uint32_t shuffle(uint32_t);
extern void packed_induction(uint8_t *, uint32_t);
int benchmark(void) {
  uint32_t seed = 0x9e3779b9u;
  uint8_t induction[256];
  packed_induction(induction, 64);
  for (unsigned i = 0; i < sizeof induction; ++i)
    if (induction[i] != i)
      return 1;
  induction[0] = 77;
  packed_induction(induction, 0);
  if (induction[0] != 77)
    return 2;
  for (unsigned i = 0; i < 1024; ++i) {
    int16_t x[4], y[4], out[4];
    x[1] = seed;
    x[2] = seed >> 16;
    y[1] = seed >> 3;
    y[2] = seed >> 9;
    dsp(x + 1, y + 1, out + 1);
    for (unsigned lane = 1; lane <= 2; ++lane) {
      int32_t product = (int32_t)x[lane] * 12345;
      uint16_t expected = (uint16_t)((product >> 15) + y[lane]);
      if ((uint16_t)out[lane] != expected)
        return 3;
    }
    uint8_t bytes[4] = {0, seed, seed >> 8, 0}, result[4] = {99, 99, 99, 99};
    narrow(bytes + 1, result + 1);
    if (result[0] != 99 || result[3] != 99)
      return 4;
    if (result[1] != (bytes[1] > 127 ? bytes[1] : 7))
      return 5;
    if (result[2] != (bytes[2] > 3 ? bytes[2] : 9))
      return 6;
    uint32_t expected = (seed >> 24) | ((seed >> 24) << 8) |
                        (seed & 0xff0000u) | ((seed & 0xff00u) << 16);
    if (shuffle(seed) != expected)
      return 7;
    seed ^= seed << 13;
    seed ^= seed >> 17;
    seed ^= seed << 5;
  }
  return 0;
}
int verify_benchmark(int result) { return result == 0; }
void initialise_benchmark(void) {}
void warm_caches(int n) {
  while (n-- > 0)
    benchmark();
}

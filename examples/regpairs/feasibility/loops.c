// SPDX-License-Identifier: Apache-2.0
// Ordinary loops for comparing xregpairs with native LLVM 23 RVP support.
#include <stdint.h>
void add_words(uint32_t *restrict d, const uint32_t *restrict a,
               const uint32_t *restrict b, unsigned n) {
  for (unsigned i = 0; i < n; ++i) d[i] = a[i] + b[i];
}
uint64_t scalar_add(uint64_t a, uint64_t b) { return a + b; }
uint64_t scalar_sub(uint64_t a, uint64_t b) { return a - b; }
// Diagnostic experiment: forcing width proves lowering, not profitability.
void forced_add_words(uint32_t *restrict d, const uint32_t *restrict a,
                      const uint32_t *restrict b, unsigned n) {
#pragma clang loop vectorize_width(2) vectorize(enable)
  for (unsigned i = 0; i < n; ++i) d[i] = a[i] + b[i];
}

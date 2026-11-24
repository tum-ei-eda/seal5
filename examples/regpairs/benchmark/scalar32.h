// SPDX-License-Identifier: Apache-2.0
// Prototype instructions injected explicitly; no automatic selection claim.
static __attribute__((always_inline)) inline uint64_t
scalar32_ror64(uint64_t x, unsigned n) {
  uint32_t lo = x, hi = x >> 32, l, h;
  if (n >= 32) {
    uint32_t t = lo;
    lo = hi;
    hi = t;
  }
  if (!(n & 31))
    return (uint64_t)hi << 32 | lo;
  __asm__(".insn r 0x0b, 0, %3, %0, %1, %2"
          : "=r"(l)
          : "r"(lo), "r"(hi), "i"(n & 31));
  __asm__(".insn r 0x0b, 0, %3, %0, %1, %2"
          : "=r"(h)
          : "r"(hi), "r"(lo), "i"(n & 31));
  return (uint64_t)h << 32 | l;
}
#define SCALAR32_SHA_FN(name, low, high)                                       \
  static __attribute__((always_inline)) inline uint64_t name(uint64_t x) {     \
    uint32_t a = x, b = x >> 32, l, h;                                         \
    __asm__(low " %0, %1, %2" : "=r"(l) : "r"(a), "r"(b));                     \
    __asm__(high " %0, %1, %2" : "=r"(h) : "r"(b), "r"(a));                    \
    return (uint64_t)h << 32 | l;                                              \
  }
SCALAR32_SHA_FN(scalar32_sig0, "sha512sig0l", "sha512sig0h")
SCALAR32_SHA_FN(scalar32_sig1, "sha512sig1l", "sha512sig1h")
SCALAR32_SHA_FN(scalar32_sum0, "sha512sum0r", "sha512sum0r")
SCALAR32_SHA_FN(scalar32_sum1, "sha512sum1r", "sha512sum1r")
#undef SCALAR32_SHA_FN

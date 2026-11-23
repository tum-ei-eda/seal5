// SPDX-License-Identifier: Apache-2.0
// SHA-512 abc known-answer check; measure only the compression call.
#include <stddef.h>
#include <stdint.h>
typedef struct {
  uint64_t total[2], state[8];
  unsigned char buffer[128];
  int is384;
} ctx_t;
extern int mbedtls_internal_sha512_process(ctx_t *, const unsigned char *);
void mbedtls_platform_zeroize(void *p, size_t n) {
  volatile unsigned char *q = p;
  while (n--)
    *q++ = 0;
}
static uint64_t iv[8] = {0x6a09e667f3bcc908ULL, 0xbb67ae8584caa73bULL,
                         0x3c6ef372fe94f82bULL, 0xa54ff53a5f1d36f1ULL,
                         0x510e527fade682d1ULL, 0x9b05688c2b3e6c1fULL,
                         0x1f83d9abfb41bd6bULL, 0x5be0cd19137e2179ULL};
static uint64_t expected[8] = {0xddaf35a193617abaULL, 0xcc417349ae204131ULL,
                               0x12e6fa4e89a97ea2ULL, 0x0a9eeee64b55d39aULL,
                               0x2192992a274fc1a8ULL, 0x36ba3c23a3feebbdULL,
                               0x454d4423643ce80eULL, 0x2a9ac94fa54ca49fULL};
static unsigned char block[128] = {'a', 'b', 'c', 0x80, [127] = 24};
int seal5_main(void) {
  ctx_t c;
  for (int i = 0; i < 8; i++)
    c.state[i] = iv[i];
  unsigned begin, end;
  __asm__ volatile("rdinstret %0" : "=r"(begin)::"memory");
  int ret = mbedtls_internal_sha512_process(&c, block);
  __asm__ volatile("rdinstret %0" : "=r"(end)::"memory");
  unsigned di = end - begin;
  __asm__ volatile(".insn r 0x2b, 7, 1, x0, %0, %1" ::"r"(di), "r"(di)
                   : "memory");
  for (int i = 0; i < 8; i++)
    if (c.state[i] != expected[i])
      return 1;
  return ret;
}

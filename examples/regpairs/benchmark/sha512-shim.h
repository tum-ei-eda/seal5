/* Extracted from Mbed TLS 2.28.10 library/sha512.c.
 * Copyright The Mbed TLS Contributors
 * SPDX-License-Identifier: Apache-2.0 OR GPL-2.0-or-later
 * Compression routine and constants are unchanged; dependency shims below.
 */
#include <stddef.h>
#include <stdint.h>
typedef struct {
  uint64_t total[2], state[8];
  unsigned char buffer[128];
  int is384;
} mbedtls_sha512_context;
#define UL64(x) x##ULL
#define SHA512_VALIDATE_RET(x) ((void)0)
static inline uint64_t get_be(const unsigned char *p) {
  return (uint64_t)p[0] << 56 | (uint64_t)p[1] << 48 | (uint64_t)p[2] << 40 |
         (uint64_t)p[3] << 32 | (uint64_t)p[4] << 24 | (uint64_t)p[5] << 16 |
         (uint64_t)p[6] << 8 | (uint64_t)p[7];
}
#define MBEDTLS_GET_UINT64_BE(data, offset) get_be((data) + (offset))
extern void mbedtls_platform_zeroize(void *, size_t);

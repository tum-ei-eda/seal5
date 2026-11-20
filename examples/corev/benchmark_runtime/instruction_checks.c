// SPDX-License-Identifier: Apache-2.0
// Compile with baseline RV32IM GCC: raw encodings keep the reference independent
// of both SEAL5 instruction selection and the assembler's custom mnemonics.
#include <stdint.h>
#include <stdio.h>

typedef uint32_t (*operation)(uint32_t, uint32_t);
#define REGISTERS ((10u << 15) | (10u << 7))
#define R(f7, f3, opcode) (((uint32_t)(f7) << 25) | (11u << 20) | REGISTERS | ((f3) << 12) | (opcode))
#define RAW(name, word)                                                        \
  static __attribute__((noinline)) uint32_t name(uint32_t x, uint32_t y) {       \
    register uint32_t a asm("a0") = x;                                         \
    register uint32_t b asm("a1") = y;                                         \
    asm volatile(".word %2" : "+r"(a) : "r"(b), "i"(word));                  \
    return a;                                                                 \
  }
#define CLIP(n)                                                               \
  RAW(clip_##n, (0x7000302bu | REGISTERS | ((n) << 20)))                         \
  RAW(clipu_##n, (0x7200302bu | REGISTERS | ((n) << 20)))
CLIP(0) CLIP(1) CLIP(2) CLIP(3) CLIP(4) CLIP(5) CLIP(6) CLIP(7)
CLIP(8) CLIP(9) CLIP(10) CLIP(11) CLIP(12) CLIP(13) CLIP(14) CLIP(15)
CLIP(16) CLIP(17) CLIP(18) CLIP(19) CLIP(20) CLIP(21) CLIP(22) CLIP(23)
CLIP(24) CLIP(25) CLIP(26) CLIP(27) CLIP(28) CLIP(29) CLIP(30) CLIP(31)
RAW(clipr, R(0x3a, 3, 0x2b))
RAW(clipur, R(0x3b, 3, 0x2b))
RAW(ror, R(0x20, 3, 0x2b))
RAW(ff1, R(0x21, 3, 0x2b) & ~(31u << 20))
RAW(fl1, R(0x22, 3, 0x2b) & ~(31u << 20))
RAW(cnt, R(0x24, 3, 0x2b) & ~(31u << 20))
RAW(bclrr, R(0x1c, 3, 0x2b))
RAW(bsetr, R(0x1d, 3, 0x2b))
RAW(insertr, R(0x1a, 3, 0x2b))
RAW(shuffle_h, R(0x60, 0, 0x7b))
RAW(shuffle_b, R(0x60, 1, 0x7b))
RAW(pack, R(0x78, 0, 0x7b))
RAW(pack_h, R(0x79, 0, 0x7b))
RAW(packhi_b, R(0x7d, 1, 0x7b))
RAW(packlo_b, R(0x7c, 1, 0x7b))
#define SHUFFLE(n) RAW(shuffle_##n, (0xc000607bu | REGISTERS | (((n)&1u) << 25) | (((n) >> 1) << 20)))
SHUFFLE(0) SHUFFLE(1) SHUFFLE(2) SHUFFLE(3)
#define BITREV(n, s) RAW(bitrev_##n##_##s, (0xc000105bu | REGISTERS | ((n) << 25) | ((s) << 20)))
BITREV(0, 0) BITREV(0, 4) BITREV(0, 31)
BITREV(1, 0) BITREV(1, 4) BITREV(1, 31)
BITREV(2, 0) BITREV(2, 4) BITREV(2, 31)

#define CLIP_ENTRY(n) {clip_##n, clipu_##n}
static operation clips[32][2] = {
    CLIP_ENTRY(0), CLIP_ENTRY(1), CLIP_ENTRY(2), CLIP_ENTRY(3),
    CLIP_ENTRY(4), CLIP_ENTRY(5), CLIP_ENTRY(6), CLIP_ENTRY(7),
    CLIP_ENTRY(8), CLIP_ENTRY(9), CLIP_ENTRY(10), CLIP_ENTRY(11),
    CLIP_ENTRY(12), CLIP_ENTRY(13), CLIP_ENTRY(14), CLIP_ENTRY(15),
    CLIP_ENTRY(16), CLIP_ENTRY(17), CLIP_ENTRY(18), CLIP_ENTRY(19),
    CLIP_ENTRY(20), CLIP_ENTRY(21), CLIP_ENTRY(22), CLIP_ENTRY(23),
    CLIP_ENTRY(24), CLIP_ENTRY(25), CLIP_ENTRY(26), CLIP_ENTRY(27),
    CLIP_ENTRY(28), CLIP_ENTRY(29), CLIP_ENTRY(30), CLIP_ENTRY(31)};
static operation reversals[3][3] = {
    {bitrev_0_0, bitrev_0_4, bitrev_0_31},
    {bitrev_1_0, bitrev_1_4, bitrev_1_31},
    {bitrev_2_0, bitrev_2_4, bitrev_2_31}};
static operation shuffles[] = {shuffle_0, shuffle_1, shuffle_2, shuffle_3};
static unsigned checks, failures;
static uint32_t beq_minus_one(uint32_t x) {
  register uint32_t input asm("a0") = x;
  uint32_t result;
  asm volatile("li %0, 1\n.word 0x01f5640b\nli %0, 0"
               : "=&r"(result) : "r"(input));
  return result;
}
static uint32_t bne_minus_one(uint32_t x) {
  register uint32_t input asm("a0") = x;
  uint32_t result;
  asm volatile("li %0, 1\n.word 0x01f5740b\nli %0, 0"
               : "=&r"(result) : "r"(input));
  return result;
}
static uint32_t random_state = 1;
static uint32_t random_word(void) {
  random_state = random_state * 1664525u + 1013904223u;
  return random_state;
}
static void check(const char *name, uint32_t got, uint32_t expected) {
  ++checks;
  if (got != expected) {
    if (failures < 20)
      printf("FAIL %s got=%08lx expected=%08lx\n", name, (unsigned long)got,
             (unsigned long)expected);
    ++failures;
  }
}
static uint32_t clamp(uint32_t x, int32_t lo, int32_t hi) {
  int32_t value = (int32_t)x;
  return value < lo ? (uint32_t)lo : value > hi ? (uint32_t)hi : x;
}
static uint32_t reverse_groups(uint32_t value, unsigned group, unsigned shift) {
  value <<= shift;
  uint32_t result = 0;
  unsigned width = 32 % group;
  if (!width) width = group;
  for (unsigned base = 0; base < 32; base += width, width = group)
    result |= ((value >> base) & ((1u << width) - 1)) << (32 - base - width);
  return result;
}
void initialise_benchmark(void) { checks = failures = 0; random_state = 1; }
void warm_caches(int heat) { (void)heat; }
int benchmark(void) {
  uint32_t edges[] = {0, 1, 0xffffffffu, 0x80000000u, 0x7fffffffu,
                      0x80017fffu, 0xc64a5933u, 0x12345678u};
  for (unsigned n = 0; n < 32; ++n) {
    int32_t hi = n ? (int32_t)((1u << (n - 1)) - 1) : 0;
    int32_t lo = -hi - 1;
    uint32_t values[] = {(uint32_t)lo, (uint32_t)hi, (uint32_t)lo - 1,
                         (uint32_t)hi + 1, 0x80000000u, 0x7fffffffu, 0xffffffffu, 0};
    for (unsigned i = 0; i < 8; ++i) {
      check("clip", clips[n][0](values[i], 0), clamp(values[i], lo, hi));
      check("clipu", clips[n][1](values[i], 0), clamp(values[i], 0, hi));
    }
  }
  for (unsigned i = 0; i < 136; ++i) {
    uint32_t x = i < 8 ? edges[i] : random_word(), y = random_word();
    check("beqimm -1", beq_minus_one(x), x == 0xffffffffu);
    check("bneimm -1", bne_minus_one(x), x != 0xffffffffu);
    int32_t hi = (int32_t)(y & 0x7fffffffu);
    check("clipr", clipr(x, y), clamp(x, -hi - 1, hi));
    check("clipur", clipur(x, y), clamp(x, 0, hi));
    unsigned shift = y & 31;
    check("ror", ror(x, y), shift ? (x >> shift) | (x << (32 - shift)) : x);
    unsigned first = 32, last = 32, count = 0;
    for (unsigned b = 0; b < 32; ++b)
      if ((x >> b) & 1) { if (first == 32) first = b; last = b; ++count; }
    check("ff1", ff1(x, 0), first);
    check("fl1", fl1(x, 0), last);
    check("cnt", cnt(x, 0), count);
    unsigned offset = y & 31, width = ((y >> 5) & 31) + 1;
    if (width > 32 - offset) width = 32 - offset;
    uint32_t low = width == 32 ? 0xffffffffu : (1u << width) - 1;
    uint32_t mask = low << offset;
    check("bclrr", bclrr(x, y), x & ~mask);
    check("bsetr", bsetr(x, y), x | mask);
    check("insertr", insertr(x, y), (x & ~mask) | ((x << offset) & mask));
    for (unsigned g = 0; g < 3; ++g)
      for (unsigned s = 0; s < 3; ++s) {
        unsigned amount = s == 0 ? 0 : s == 1 ? 4 : 31;
        check("bitrev", reversals[g][s](x, 0), reverse_groups(x, g + 1, amount));
      }
    uint32_t shuffled = ((x >> ((y & 1) * 16)) & 65535u) |
                        ((x >> (((y >> 16) & 1) * 16)) << 16);
    check("shuffle.h rd=rs1", shuffle_h(x, y), shuffled);
    shuffled = 0;
    for (unsigned lane = 0; lane < 4; ++lane)
      shuffled |= ((x >> (((y >> (8 * lane)) & 3) * 8)) & 255u) << (8 * lane);
    check("shuffle.b rd=rs1", shuffle_b(x, y), shuffled);
    check("pack rd=rs1", pack(x, y), (x << 16) | (y & 65535u));
    check("pack.h rd=rs1", pack_h(x, y), (x & 0xffff0000u) | (y >> 16));
    check("packhi.b rd=rs1", packhi_b(x, y), ((x & 255u) << 24) | ((y & 255u) << 16) | (x & 65535u));
    check("packlo.b rd=rs1", packlo_b(x, y), (x & 0xffff0000u) | ((x & 255u) << 8) | (y & 255u));
    for (unsigned selector = 0; selector < 4; ++selector) {
      shuffled = ((x >> ((selector & 1) * 16)) & 65535u) |
                 ((x >> (((selector >> 1) & 1) * 16)) << 16);
      check("shuffle.sci.h rd=rs1", shuffles[selector](x, 0), shuffled);
    }
  }
  printf("COREV_CHECKS checks=%u failures=%u\n", checks, failures);
  return failures;
}
int verify_benchmark(int result) { return result == 0; }

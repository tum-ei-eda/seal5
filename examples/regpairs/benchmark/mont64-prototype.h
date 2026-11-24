// SPDX-License-Identifier: Apache-2.0
// Explicit prototype selection using LLVM's R constraint for even/odd pairs.
// custom-2 funct3=0: upper half of (a::b)<<1; funct3=1: unsigned a>=b.
static __attribute__((always_inline)) inline uint64_t mont_fsl1(uint64_t a,
                                                                uint64_t b) {
  uint64_t result;
  __asm__(".insn r 0x5b, 0, 0, %0, %1, %2" : "=R"(result) : "R"(a), "R"(b));
  return result;
}
static __attribute__((always_inline)) inline unsigned mont_geu(uint64_t a,
                                                               uint64_t b) {
  unsigned result;
  __asm__(".insn r 0x5b, 1, 0, %0, %1, %2" : "=r"(result) : "R"(a), "R"(b));
  return result;
}

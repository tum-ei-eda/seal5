// SPDX-License-Identifier: Apache-2.0
#include "support.h"
#include <stdint.h>
#include <stdio.h>

// ETISS's host-side instruction counter uses these symbols as ROI boundaries.
__attribute__((noinline, noclone)) void seal5_measure_start(void) {
  __asm__ volatile("nop" ::: "memory");
}
__attribute__((noinline, noclone)) void seal5_measure_end(void) {
  __asm__ volatile("nop\nnop" ::: "memory");
}

int main(void) {
  initialise_benchmark();
  warm_caches(1);
  seal5_measure_start();
  int result = benchmark();
  seal5_measure_end();
  int verified = verify_benchmark(result) == 1;
  printf("SEAL5_RESULT verified=%d\n", verified);
  return verified ? 0 : 1;
}

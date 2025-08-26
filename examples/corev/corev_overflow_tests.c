#include <stdint.h>
#include <stdio.h>

uint32_t avg(uint32_t x, uint32_t y) { // should match to cv.addun
    return (x + y) >> 1;
}

uint32_t avg2(uint32_t x, uint32_t y) { // should NOT match to cv.addun
    return ((uint64_t)x + y) >> 1;
}

uint32_t avg3(uint32_t x, uint32_t y) { // should NOT match to cv.addun
    return (((uint64_t)x + y) & 0x1ffffffff) >> 1;
}

uint32_t fixed_point_multiply_accumulate_unsigned_half(uint16_t x, uint16_t y, uint32_t acc) { // should NOT match to cv.macun
    return (acc + x * y) >> 7;
}

uint32_t fixed_point_multiply_accumulate_unsigned_half2(uint16_t x, uint16_t y, uint32_t acc) { // should match to cv.macun
    return ((uint64_t)acc + x * y) >> 7;
}

uint32_t fixed_point_multiply_accumulate_unsigned_half3(uint16_t x, uint16_t y, uint32_t acc) { // should match to cv.macun
    return (((uint64_t)acc + x * y) & 0x1ffffffff) >> 7;
}

uint32_t fixed_point_multiply_accumulate_unsigned_half_round(uint16_t x, uint16_t y, uint32_t acc) { // should NOT match to cv.macurn
    return (acc + x * y + ((uint64_t)1<<6)) >> 7;
}

uint32_t fixed_point_multiply_accumulate_unsigned_half_round2(uint16_t x, uint16_t y, uint32_t acc) { // should match to cv.macurn
    return ((uint64_t)acc + (uint64_t)x * y + ((uint64_t)1<<6)) >> 7;
}

uint32_t fixed_point_multiply_accumulate_unsigned_half_round3(uint16_t x, uint16_t y, uint32_t acc) { // should match to cv.macurn
    return (((uint64_t)acc + (uint64_t)x * y + ((uint64_t)1<<6)) & 0x3ffffffff) >> 7;
}

uint32_t large_fixed_point_multiply_accumulate_unsigned_half(uint16_t x, uint16_t y, uint32_t acc) { // should NOT match to cv.macun
    return (acc + x * y) >> 19;
}

uint32_t large_fixed_point_multiply_accumulate_unsigned_half2(uint16_t x, uint16_t y, uint32_t acc) { // should match to cv.macun
    return ((uint64_t)acc + x * y) >> 19;
}

uint32_t large_fixed_point_multiply_accumulate_unsigned_half3(uint16_t x, uint16_t y, uint32_t acc) { // should match to cv.macun
    return (((uint64_t)acc + x * y) & 0x1ffffffff) >> 19;
}

uint32_t large_fixed_point_multiply_accumulate_unsigned_half_round(uint16_t x, uint16_t y, uint32_t acc) { // should NOT match to cv.macurn
    return (acc + x * y + ((uint64_t)1<<18)) >> 19;
}

uint32_t large_fixed_point_multiply_accumulate_unsigned_half_round2(uint16_t x, uint16_t y, uint32_t acc) { // should match to cv.macurn
    return ((uint64_t)acc + (uint64_t)x * y + ((uint64_t)1<<18)) >> 19;
}

uint32_t large_fixed_point_multiply_accumulate_unsigned_half_round3(uint16_t x, uint16_t y, uint32_t acc) { // should match to cv.macurn
    return (((uint64_t)acc + (uint64_t)x * y + ((uint64_t)1<<18)) & 0x3ffffffff) >> 19;
}

// Note: to see 34 bit usage the shift should be (1<<18) or larger

/*uint32_t fixed_point_multiply_accumulate_unsigned_word(uint32_t x, uint32_t y, uint32_t acc) {
    return (acc + x * y) >> 7;
}*/

int main() {
    printf("avg(%lu,%lu)=%u [%x]\n", 1UL, 10UL, avg(1, 10), avg(1, 10));  // Expected: floor(5.5)=5 Got: ?
    printf("avg(%lu,%lu)=%u [%x]\n", 2147483647UL, 2147483647UL, avg(2147483647, 2147483647), avg(2147483647, 2147483647));  // Expected: 2147483647 Got: ?
    printf("avg(%lu,%lu)=%u [%x]\n", 2147483648UL, 2147483648UL, avg(2147483648, 2147483648), avg(2147483648, 2147483648));  // Expected: 0 Got: ?
    printf("avg2(%lu,%lu)=%u [%x]\n", 1UL, 10UL, avg2(1, 10), avg2(1, 10));  // Expected: floor(5.5)=5 Got: ?
    printf("avg2(%lu,%lu)=%u [%x]\n", 2147483647UL, 2147483647UL, avg2(2147483647, 2147483647), avg2(2147483647, 2147483647));  // Expected: 2147483647 Got: ?
    printf("avg2(%lu,%lu)=%u [%x]\n", 2147483648UL, 2147483648UL, avg2(2147483648, 2147483648), avg2(2147483648, 2147483648));  // Expected: 2147483648 Got: ?
    printf("avg3(%lu,%lu)=%u [%x]\n", 1UL, 10UL, avg3(1, 10), avg3(1, 10));  // Expected: floor(5.5)=5 Got: ?
    printf("avg3(%lu,%lu)=%u [%x]\n", 2147483647UL, 2147483647UL, avg3(2147483647, 2147483647), avg3(2147483647, 2147483647));  // Expected: 2147483647 Got: ?
    printf("avg3(%lu,%lu)=%u [%x]\n", 2147483648UL, 2147483648UL, avg3(2147483648, 2147483648), avg3(2147483648, 2147483648));  // Expected: 2147483648 Got: ?
    printf("---\n");
    printf("fixed_point_multiply_accumulate_unsigned_half(%lu,%lu,%lu)=%u [%x]\n", 100UL, 1000UL, 9400UL, fixed_point_multiply_accumulate_unsigned_half(100, 1000, 9400), fixed_point_multiply_accumulate_unsigned_half(100, 1000, 9400));  // Expected: 854 Got: ?
    printf("fixed_point_multiply_accumulate_unsigned_half(%lu,%lu,%lu)=%u [%x]\n", 65535UL, 65535UL, 131070UL, fixed_point_multiply_accumulate_unsigned_half(65535, 65535, 131070), fixed_point_multiply_accumulate_unsigned_half(65535, 65535, 131070));  // Expected: 33554431 Got: ?
    printf("fixed_point_multiply_accumulate_unsigned_half(%lu,%lu,%lu)=%u [%x]\n", 65535UL, 65535UL, 131071UL, fixed_point_multiply_accumulate_unsigned_half(65535, 65535, 131071), fixed_point_multiply_accumulate_unsigned_half(65535, 65535, 131071));  // Expected: 0 Got: ?
    printf("fixed_point_multiply_accumulate_unsigned_half2(%lu,%lu,%lu)=%u [%x]\n", 100UL, 1000UL, 9400UL, fixed_point_multiply_accumulate_unsigned_half2(100, 1000, 9400), fixed_point_multiply_accumulate_unsigned_half2(100, 1000, 9400));  // Expected: 854 Got: ?
    printf("fixed_point_multiply_accumulate_unsigned_half2(%lu,%lu,%lu)=%u [%x]\n", 65535UL, 65535UL, 131070UL, fixed_point_multiply_accumulate_unsigned_half2(65535, 65535, 131070), fixed_point_multiply_accumulate_unsigned_half2(65535, 65535, 131070));  // Expected: 4294967295 Got: ?
    printf("fixed_point_multiply_accumulate_unsigned_half2(%lu,%lu,%lu)=%u [%x]\n", 65535UL, 65535UL, 131071UL, fixed_point_multiply_accumulate_unsigned_half2(65535, 65535, 131071), fixed_point_multiply_accumulate_unsigned_half2(65535, 65535, 131071));  // Expected: 0 Got: ?
    printf("fixed_point_multiply_accumulate_unsigned_half3(%lu,%lu,%lu)=%u [%x]\n", 100UL, 1000UL, 9400UL, fixed_point_multiply_accumulate_unsigned_half3(100, 1000, 9400), fixed_point_multiply_accumulate_unsigned_half3(100, 1000, 9400));  // Expected: 854 Got: ?
    printf("fixed_point_multiply_accumulate_unsigned_half3(%lu,%lu,%lu)=%u [%x]\n", 65535UL, 65535UL, 131070UL, fixed_point_multiply_accumulate_unsigned_half3(65535, 65535, 131070), fixed_point_multiply_accumulate_unsigned_half3(65535, 65535, 131070));  // Expected: 4294967295 Got: ?
    printf("fixed_point_multiply_accumulate_unsigned_half3(%lu,%lu,%lu)=%u [%x]\n", 65535UL, 65535UL, 131071UL, fixed_point_multiply_accumulate_unsigned_half3(65535, 65535, 131071), fixed_point_multiply_accumulate_unsigned_half3(65535, 65535, 131071));  // Expected: 0 Got: ?
    printf("---\n");
    printf("fixed_point_multiply_accumulate_unsigned_half_round(%lu,%lu,%lu)=%u [%x]\n", 100UL, 1000UL, 9400UL, fixed_point_multiply_accumulate_unsigned_half_round(100, 1000, 9400), fixed_point_multiply_accumulate_unsigned_half_round(100, 1000, 9400));  // Expected: 855 Got: ?
    printf("fixed_point_multiply_accumulate_unsigned_half_round(%lu,%lu,%lu)=%u [%x]\n", 65535UL, 65535UL, 4294967295UL, fixed_point_multiply_accumulate_unsigned_half_round(65535, 65535, 4294967295UL), fixed_point_multiply_accumulate_unsigned_half_round(65535, 65535, 4294967295UL));  // Expected: 0 Got: ?
    printf("fixed_point_multiply_accumulate_unsigned_half_round2(%lu,%lu,%lu)=%u [%x]\n", 100UL, 1000UL, 9400UL, fixed_point_multiply_accumulate_unsigned_half_round2(100, 1000, 9400), fixed_point_multiply_accumulate_unsigned_half_round2(100, 1000, 9400));  // Expected: 855 Got: ?
    printf("fixed_point_multiply_accumulate_unsigned_half_round2(%lu,%lu,%lu)=%u [%x]\n", 65535UL, 65535UL, 4294967295UL, fixed_point_multiply_accumulate_unsigned_half_round2(65535, 65535, 4294967295UL), fixed_point_multiply_accumulate_unsigned_half_round2(65535, 65535, 4294967295UL));  // Expected: 0 Got: ?
    printf("fixed_point_multiply_accumulate_unsigned_half_round3(%lu,%lu,%lu)=%u [%x]\n", 100UL, 1000UL, 9400UL, fixed_point_multiply_accumulate_unsigned_half_round3(100, 1000, 9400), fixed_point_multiply_accumulate_unsigned_half_round3(100, 1000, 9400));  // Expected: 855 Got: ?
    printf("fixed_point_multiply_accumulate_unsigned_half_round3(%lu,%lu,%lu)=%u [%x]\n", 65535UL, 65535UL, 4294967295UL, fixed_point_multiply_accumulate_unsigned_half_round3(65535, 65535, 4294967295UL), fixed_point_multiply_accumulate_unsigned_half_round3(65535, 65535, 4294967295UL));  // Expected: 0 Got: ?
    printf("---\n");
    printf("large_fixed_point_multiply_accumulate_unsigned_half(%lu,%lu,%lu)=%u [%x]\n", 100UL, 1000UL, 9400UL, large_fixed_point_multiply_accumulate_unsigned_half(100, 1000, 9400), large_fixed_point_multiply_accumulate_unsigned_half(100, 1000, 9400));  // Expected: 854 Got: ?
    printf("large_fixed_point_multiply_accumulate_unsigned_half(%lu,%lu,%lu)=%u [%x]\n", 65535UL, 65535UL, 131070UL, large_fixed_point_multiply_accumulate_unsigned_half(65535, 65535, 131070), large_fixed_point_multiply_accumulate_unsigned_half(65535, 65535, 131070));  // Expected: 33554431 Got: ?
    printf("large_fixed_point_multiply_accumulate_unsigned_half(%lu,%lu,%lu)=%u [%x]\n", 65535UL, 65535UL, 131071UL, large_fixed_point_multiply_accumulate_unsigned_half(65535, 65535, 131071), large_fixed_point_multiply_accumulate_unsigned_half(65535, 65535, 131071));  // Expected: 0 Got: ?
    printf("large_fixed_point_multiply_accumulate_unsigned_half2(%lu,%lu,%lu)=%u [%x]\n", 100UL, 1000UL, 9400UL, large_fixed_point_multiply_accumulate_unsigned_half2(100, 1000, 9400), large_fixed_point_multiply_accumulate_unsigned_half2(100, 1000, 9400));  // Expected: 854 Got: ?
    printf("large_fixed_point_multiply_accumulate_unsigned_half2(%lu,%lu,%lu)=%u [%x]\n", 65535UL, 65535UL, 131070UL, large_fixed_point_multiply_accumulate_unsigned_half2(65535, 65535, 131070), large_fixed_point_multiply_accumulate_unsigned_half2(65535, 65535, 131070));  // Expected: 4294967295 Got: ?
    printf("large_fixed_point_multiply_accumulate_unsigned_half2(%lu,%lu,%lu)=%u [%x]\n", 65535UL, 65535UL, 131071UL, large_fixed_point_multiply_accumulate_unsigned_half2(65535, 65535, 131071), large_fixed_point_multiply_accumulate_unsigned_half2(65535, 65535, 131071));  // Expected: 0 Got: ?
    printf("large_fixed_point_multiply_accumulate_unsigned_half3(%lu,%lu,%lu)=%u [%x]\n", 100UL, 1000UL, 9400UL, large_fixed_point_multiply_accumulate_unsigned_half3(100, 1000, 9400), large_fixed_point_multiply_accumulate_unsigned_half3(100, 1000, 9400));  // Expected: 854 Got: ?
    printf("large_fixed_point_multiply_accumulate_unsigned_half3(%lu,%lu,%lu)=%u [%x]\n", 65535UL, 65535UL, 131070UL, large_fixed_point_multiply_accumulate_unsigned_half3(65535, 65535, 131070), large_fixed_point_multiply_accumulate_unsigned_half3(65535, 65535, 131070));  // Expected: 4294967295 Got: ?
    printf("large_fixed_point_multiply_accumulate_unsigned_half3(%lu,%lu,%lu)=%u [%x]\n", 65535UL, 65535UL, 131071UL, large_fixed_point_multiply_accumulate_unsigned_half3(65535, 65535, 131071), large_fixed_point_multiply_accumulate_unsigned_half3(65535, 65535, 131071));  // Expected: 0 Got: ?
    printf("---\n");
    printf("large_fixed_point_multiply_accumulate_unsigned_half_round(%lu,%lu,%lu)=%u [%x]\n", 100UL, 1000UL, 9400UL, large_fixed_point_multiply_accumulate_unsigned_half_round(100, 1000, 9400), large_fixed_point_multiply_accumulate_unsigned_half_round(100, 1000, 9400));  // Expected: 855 Got: ?
    printf("large_fixed_point_multiply_accumulate_unsigned_half_round(%lu,%lu,%lu)=%u [%x]\n", 65535UL, 65535UL, 4294967295UL, large_fixed_point_multiply_accumulate_unsigned_half_round(65535, 65535, 4294967295UL), large_fixed_point_multiply_accumulate_unsigned_half_round(65535, 65535, 4294967295UL));  // Expected: 0 Got: ?
    printf("large_fixed_point_multiply_accumulate_unsigned_half_round2(%lu,%lu,%lu)=%u [%x]\n", 100UL, 1000UL, 9400UL, large_fixed_point_multiply_accumulate_unsigned_half_round2(100, 1000, 9400), large_fixed_point_multiply_accumulate_unsigned_half_round2(100, 1000, 9400));  // Expected: 855 Got: ?
    printf("large_fixed_point_multiply_accumulate_unsigned_half_round2(%lu,%lu,%lu)=%u [%x]\n", 65535UL, 65535UL, 4294967295UL, large_fixed_point_multiply_accumulate_unsigned_half_round2(65535, 65535, 4294967295UL), large_fixed_point_multiply_accumulate_unsigned_half_round2(65535, 65535, 4294967295UL));  // Expected: 0 Got: ?
    printf("large_fixed_point_multiply_accumulate_unsigned_half_round3(%lu,%lu,%lu)=%u [%x]\n", 100UL, 1000UL, 9400UL, large_fixed_point_multiply_accumulate_unsigned_half_round3(100, 1000, 9400), large_fixed_point_multiply_accumulate_unsigned_half_round3(100, 1000, 9400));  // Expected: 855 Got: ?
    printf("large_fixed_point_multiply_accumulate_unsigned_half_round3(%lu,%lu,%lu)=%u [%x]\n", 65535UL, 65535UL, 4294967295UL, large_fixed_point_multiply_accumulate_unsigned_half_round3(65535, 65535, 4294967295UL), large_fixed_point_multiply_accumulate_unsigned_half_round3(65535, 65535, 4294967295UL));  // Expected: 0 Got: ?
}

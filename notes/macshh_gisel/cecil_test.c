#include <stdint.h>

// uint32_t test_maxu32(uint32_t x, uint32_t y) {
//     return (x > y) ? x : y;
// }
//
// uint16_t test_maxu16(uint16_t x, uint16_t y) {
//     return (x > y) ? x : y;
// }
//
// uint8_t test_maxu8(uint8_t x, uint8_t y) {
//     return (x > y) ? x : y;
// }
//
// int32_t test_maxs32(int32_t x, int32_t y) {
//     return (x > y) ? x : y;
// }
//
// int16_t test_maxs16(int16_t x, int16_t y) {
//     return (x > y) ? x : y;
// }
//
// int8_t test_maxs8(int8_t x, int8_t y) {
//     return (x > y) ? x : y;
// }
//
// uint32_t test_minu32(uint32_t x, uint32_t y) {
//     return (x < y) ? x : y;
// }
//
// uint16_t test_minu16(uint16_t x, uint16_t y) {
//     return (x < y) ? x : y;
// }
//
// uint8_t test_minu8(uint8_t x, uint8_t y) {
//     return (x < y) ? x : y;
// }
//
// int32_t test_mins32(int32_t x, int32_t y) {
//     return (x < y) ? x : y;
// }
//
// int16_t test_mins16(int16_t x, int16_t y) {
//     return (x < y) ? x : y;
// }
//
// int8_t test_mins8(int8_t x, int8_t y) {
//     return (x < y) ? x : y;
// }
//
// int32_t test_abs32(int32_t x) {
//     return (x > 0) ? x : -x;
// }
//
// int16_t test_abs16(int16_t x) {
//     return (x > 0) ? x : -x;
// }
//
// int8_t test_abs8(int8_t x) {
//     return (x > 0) ? x : -x;
// }
//
// int32_t test_mac32(int32_t acc, int32_t x, int32_t y) {
//     return acc + x * y;
// }
//
// int32_t test_macs32_16(int32_t acc, int16_t x, int16_t y) {
//     return acc + x * y;
// }
//
int32_t test_macs32_v2i16(int32_t acc, int32_t x, int32_t y) {
    acc += (int32_t)(int16_t)(x & 0xffff) * (int32_t)(int16_t)(y & 0xffff);
    acc += (int32_t)(int16_t)((x >> 16) & 0xffff) * (int32_t)(int16_t)((y >> 16) & 0xffff);
    return acc;
}
//
// uint32_t test_macu32_16(uint32_t acc, uint16_t x, uint16_t y) {
//     return acc + x * y;
// }
//
// int32_t test_macs32_8(int32_t acc, int8_t x, int8_t y) {
//     return acc + x * y;
// }
//
// uint32_t test_macu32_8(uint32_t acc, uint8_t x, uint8_t y) {
//     return acc + x * y;
// }
//
// int32_t test_msu32(int32_t acc, int32_t x, int32_t y) {
//     return acc - x * y;
// }
//
// int32_t test_msus32_16(int32_t acc, int16_t x, int16_t y) {
//     return acc - x * y;
// }
//
// uint32_t test_msuu32_16(uint32_t acc, uint16_t x, uint16_t y) {
//     return acc - x * y;
// }
//
// int32_t test_msus32_8(int32_t acc, int8_t x, int8_t y) {
//     return acc - x * y;
// }
//
// uint32_t test_msuu32_8(uint32_t acc, uint8_t x, uint8_t y) {
//     return acc - x * y;
// }
//
// int32_t test_slets(int32_t x, int32_t y) {
//     return x <= y;
// }
//
// int32_t test_sletu(uint32_t x, uint32_t y) {
//     return x <= y;
// }
//
// int32_t test_addns(int32_t x, int32_t y) {
//     return (x + y) >> 8;
// }
//
// uint32_t test_addnu(uint32_t x, uint32_t y) {
//     return (x + y) >> 8;
// }

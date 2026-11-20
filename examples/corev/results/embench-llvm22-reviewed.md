# LLVM 22 SEAL5 CORE-V Embench

RV32IM/ILP32, strict alignment, O3, normal vectorizer profitability, no LTO; GlobalISel with fallback disabled.

Independent host-side instruction instrumentation between seal5_measure_start/end; includes marker/call overhead. ETISS cycles are a model, not hardware timing. Initialization, warmup and verification excluded.

The same baseline GCC startup, support library and Newlib are linked into both variants. The benchmark C translation units are compiled by the same LLVM toolchain. CPU_MHZ=1 and warm_caches(1); no source changes or forced vector widths.

Instruction counts are medians over verified repetitions. Ratios include only pairs that verify. Text sizes are linked .text, including the shared runtime and libraries.

| Program | Baseline | CORE-V | Baseline instructions | CORE-V instructions | Instruction ratio (baseline / CORE-V) | Text bytes (baseline / CORE-V) |
|---|---|---|---:|---:|---:|---:|
| aha-mont64 | verified | verified | 5806645 | 5810461 | 0.9993 | 69180 / 69276 |
| crc32 | verified | verified | 4005409 | 3831336 | 1.0454 | 65596 / 65628 |
| cubic | compile_failed | compile_failed | — | — | — | — / — |
| edn | verified | verified | 3220984 | 2506471 | 1.2851 | 68732 / 68300 |
| huffbench | verified | verified | 2519750 | 2406189 | 1.0472 | 67836 / 67692 |
| matmult-int | verified | verified | 1997869 | 1669020 | 1.1970 | 67532 / 67500 |
| md5sum | verified | verified | 2019904 | 1946773 | 1.0376 | 66412 / 66492 |
| minver | verified | verified | 5017804 | 5020584 | 0.9994 | 72520 / 72584 |
| nbody | verified | verified | 3436375 | 3454939 | 0.9946 | 70740 / 71348 |
| nettle-aes | verified | verified | 3871746 | 3271308 | 1.1835 | 69916 / 69868 |
| nettle-sha256 | verified | verified | 4413263 | 3409118 | 1.2945 | 73676 / 72492 |
| nsichneu | verified | verified | 2001632 | 2001637 | 1.0000 | 82124 / 81660 |
| picojpeg | verified | verified | 3296200 | 3270029 | 1.0080 | 94268 / 95260 |
| primecount | verified | verified | 4571595 | 4081141 | 1.1202 | 65820 / 65788 |
| qrduino | verified | verified | 2838449 | 2717027 | 1.0447 | 84236 / 85404 |
| sglib-combined | verified | verified | 2383411 | 2281689 | 1.0446 | 77436 / 77628 |
| slre | verified | verified | 2681172 | 2905906 | 0.9227 | 70364 / 70588 |
| st | verified | verified | 3835252 | 3837967 | 0.9993 | 69600 / 69760 |
| statemate | verified | verified | 1154863 | 1160760 | 0.9949 | 69724 / 70044 |
| tarfind | verified | verified | 1209286 | 1175024 | 1.0292 | 66492 / 66492 |
| ud | verified | verified | 2057433 | 1897809 | 1.0841 | 66636 / 66684 |
| wikisort | verified | verified | 1065226 | 1083175 | 0.9834 | 77316 / 78292 |

Geometric mean instruction ratio over 21 verified pairs: 1.0585.

## Executed custom instructions

- aha-mont64: `cv_addrn` × 386629, `cv_and_b` × 51188, `cv_bneimm` × 27072, `cv_clip` × 162432, `cv_mac` × 12694, `cv_or_b` × 935679, `cv_subrn` × 491103, `cv_xor_b` × 27921
- crc32: `cv_addrn` × 174250, `cv_and_b` × 1, `cv_bneimm` × 174080, `cv_extbz` × 174080, `cv_lw_rr` × 174080, `cv_xor_b` × 348161
- edn: `cv_addn` × 21750, `cv_addrn` × 377155, `cv_addun` × 696, `cv_clip` × 2784, `cv_exths` × 8352, `cv_lh_rr` × 217500, `cv_mac` × 521304, `cv_msu` × 8700, `cv_subn` × 8613, `cv_subrn` × 9048, `cv_subun` × 783, `cv_sw_rr` × 4350
- huffbench: `cv_abs` × 1782, `cv_addn` × 693, `cv_addrn` × 643148, `cv_and_b` × 56650, `cv_beqimm` × 17545, `cv_bneimm` × 93060, `cv_clip` × 11, `cv_extbz` × 11, `cv_lbu_rr` × 35750, `cv_lw_rr` × 58652, `cv_maxu` × 704, `cv_or_b` × 46013, `cv_sb_rr` × 71104, `cv_subrn` × 352, `cv_sw_rr` × 16049
- matmult-int: `cv_addrn` × 39653, `cv_bneimm` × 46, `cv_lw_rr` × 18400, `cv_mac` × 351440
- md5sum: `cv_addrn` × 630564, `cv_and_b` × 91443, `cv_lw_rr` × 52224, `cv_or_b` × 39219, `cv_sb_rr` × 51051, `cv_xor_b` × 78339
- minver: `cv_addrn` × 73262, `cv_and_b` × 1665, `cv_beqimm` × 11655, `cv_bneimm` × 3885, `cv_lw_rr` × 14430, `cv_mac` × 10545, `cv_subrn` × 1665, `cv_sw_rr` × 15540, `cv_xor_b` × 4995
- nbody: `cv_addrn` × 9629, `cv_beqimm` × 501, `cv_lw_rr` × 1000
- nettle-aes: `cv_addrn` × 119190, `cv_and_b` × 156, `cv_beqimm` × 8502, `cv_bneimm` × 42354, `cv_extbz` × 437580, `cv_lbu_rr` × 48048, `cv_lw_rr` × 537888, `cv_or_b` × 69732, `cv_ror` × 13260, `cv_sw_rr` × 8112, `cv_xor_b` × 560508
- nettle-sha256: `cv_addrn` × 590426, `cv_addun` × 42750, `cv_and_b` × 182875, `cv_beqimm` × 1425, `cv_bneimm` × 475, `cv_or_b` × 47975, `cv_ror` × 547200, `cv_sb_rr` × 475, `cv_subrn` × 950, `cv_xor_b` × 668800
- nsichneu: `cv_addrn` × 1232, `cv_bneimm` × 1231
- picojpeg: `cv_addrn` × 534733, `cv_addun` × 22176, `cv_addurn` × 9984, `cv_and_b` × 9402, `cv_beqimm` × 10794, `cv_bneimm` × 31050, `cv_clip` × 1368, `cv_extbz` × 57672, `cv_exths` × 36312, `cv_exthz` × 139236, `cv_lb_rr` × 1890, `cv_lbu_rr` × 5502, `cv_lhu_rr` × 510, `cv_mac` × 6, `cv_minu` × 18, `cv_or_b` × 105438, `cv_sb_rr` × 198, `cv_sh_rr` × 64512, `cv_subrn` × 94962, `cv_suburn` × 9984
- primecount: `cv_addrn` × 977256, `cv_beqimm` × 156787, `cv_clip` × 186044, `cv_mac` × 186044, `cv_max` × 186044, `cv_maxu` × 186044, `cv_subrn` × 186044, `cv_sw_rr` × 82
- qrduino: `cv_abs` × 40, `cv_addn` × 40, `cv_addrn` × 474560, `cv_addun` × 40480, `cv_and_b` × 262715, `cv_beqimm` × 55660, `cv_bneimm` × 44530, `cv_clip` × 25005, `cv_extbs` × 1760, `cv_extbz` × 188125, `cv_lbu_rr` × 135975, `cv_lw_rr` × 5, `cv_mac` × 9645, `cv_maxu` × 10, `cv_minu` × 40, `cv_or_b` × 30940, `cv_sb_rr` × 60440, `cv_subrn` × 50, `cv_xor_b` × 109070
- sglib-combined: `cv_addrn` × 217592, `cv_beqimm` × 8265, `cv_bneimm` × 47125, `cv_extbz` × 8497, `cv_exths` × 11600, `cv_exthz` × 11774, `cv_lw_rr` × 84013, `cv_max` × 4524, `cv_msu` × 8700, `cv_or_b` × 12006, `cv_sb_rr` × 2871, `cv_subrn` × 22098, `cv_sw_rr` × 42282, `cv_xor_b` × 87
- slre: `cv_addrn` × 323071, `cv_and_b` × 21010, `cv_beqimm` × 18590, `cv_bneimm` × 5940, `cv_clip` × 6270, `cv_extbz` × 6270, `cv_lbu_rr` × 51040, `cv_max` × 8580, `cv_or_b` × 8470, `cv_sle` × 8470, `cv_subrn` × 32780, `cv_xor_b` × 6270
- st: `cv_addrn` × 14319, `cv_mac` × 2600, `cv_msu` × 2600
- statemate: `cv_addrn` × 5893, `cv_beqimm` × 53028, `cv_bneimm` × 29460, `cv_extbz` × 19640
- tarfind: `cv_addrn` × 134514, `cv_beqimm` × 4935, `cv_bneimm` × 5781, `cv_lbu_rr` × 4700, `cv_mac` × 3290, `cv_msu` × 36190
- ud: `cv_addrn` × 537992, `cv_beqimm` × 7390, `cv_bneimm` × 23648, `cv_lw_rr` × 84246, `cv_mac` × 69466, `cv_msu` × 125630, `cv_sw_rr` × 53208
- wikisort: `cv_addn` × 799, `cv_addrn` × 82038, `cv_beqimm` × 1982, `cv_bneimm` × 9, `cv_clip` × 399, `cv_lw_rr` × 8370, `cv_subrn` × 1291, `cv_sw_rr` × 6662

## Failures

- cubic / baseline: compile_failed. LLVM ERROR: unable to legalize instruction: %201:_(s32) = G_FCMP floatpred(olt), %40:_(s128), %163:_ (in function: SolveCubic)
- cubic / corev: compile_failed. LLVM ERROR: unable to legalize instruction: %201:_(s32) = G_FCMP floatpred(olt), %40:_(s128), %163:_ (in function: SolveCubic)

Full commands, source hashes, tool versions, disassembly and per-repetition counts are retained with results.json.

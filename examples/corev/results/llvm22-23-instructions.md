# LLVM 22 / LLVM 23 instruction counts

LLVM 22 uses the validated three-repeat reference; LLVM 23 uses one execution per variant for compatibility validation. All 21 pairs verify. `cubic` fails compilation on both versions and is excluded. Counts are executed instructions, not hardware cycles.

CORE-V uses **5.52% fewer instructions on LLVM 22** and **4.77% fewer on LLVM 23**, relative to each version’s matching baseline. Across versions, LLVM 23 uses 0.93% fewer baseline instructions and 0.15% fewer CORE-V instructions by geometric mean.

| Program | Baseline LLVM 22 | Baseline LLVM 23 | Change | CORE-V LLVM 22 | CORE-V LLVM 23 | Change |
|---|---:|---:|---:|---:|---:|---:|
| aha-mont64 | 5806645 | 5806647 | +0.00% | 5810461 | 5809617 | -0.01% |
| crc32 | 4005409 | 4005409 | +0.00% | 3831336 | 3831336 | +0.00% |
| edn | 3220984 | 3086045 | -4.19% | 2506471 | 2520305 | +0.55% |
| huffbench | 2519750 | 2524997 | +0.21% | 2406189 | 2411458 | +0.22% |
| matmult-int | 1997869 | 1997869 | +0.00% | 1669020 | 1669020 | +0.00% |
| md5sum | 2019904 | 2019904 | +0.00% | 1946773 | 1947589 | +0.04% |
| minver | 5017804 | 5013364 | -0.09% | 5020584 | 5020584 | +0.00% |
| nbody | 3436375 | 3436375 | +0.00% | 3454939 | 3454939 | +0.00% |
| nettle-aes | 3871746 | 3871590 | -0.00% | 3271308 | 3301806 | +0.93% |
| nettle-sha256 | 4413263 | 3935413 | -10.83% | 3409118 | 3276118 | -3.90% |
| nsichneu | 2001632 | 2001632 | +0.00% | 2001637 | 2001637 | +0.00% |
| picojpeg | 3296200 | 3375790 | +2.41% | 3270029 | 3372659 | +3.14% |
| primecount | 4571595 | 4571595 | +0.00% | 4081141 | 4081141 | +0.00% |
| qrduino | 2838449 | 2775259 | -2.23% | 2717027 | 2677877 | -1.44% |
| sglib-combined | 2383411 | 2413249 | +1.25% | 2281689 | 2305700 | +1.05% |
| slre | 2681172 | 2674462 | -0.25% | 2905906 | 2899636 | -0.22% |
| st | 3835252 | 3832643 | -0.07% | 3837967 | 3844407 | +0.17% |
| statemate | 1154863 | 1135223 | -1.70% | 1160760 | 1141120 | -1.69% |
| tarfind | 1209286 | 1209286 | +0.00% | 1175024 | 1175071 | +0.00% |
| ud | 2057433 | 2036741 | -1.01% | 1897809 | 1897809 | +0.00% |
| wikisort | 1065226 | 1039782 | -2.39% | 1083175 | 1064375 | -1.74% |

PicoJPEG grows in both variants (+2.41% baseline, +3.14% CORE-V); SGLIB also grows (+1.25% baseline, +1.05% CORE-V). These are observed performance regressions, with no verification failures. Follow-up should compare the hot functions’ optimized IR and assembly first, since both variants regress. SHA-256 and EDN improve more in the baseline than with CORE-V; inspect vectorization and instruction costs before proposing additional CORE-V changes. No speculative optimizer patches were added for these differences.

See [LLVM 23 validation](llvm23-validation.md) and the [full LLVM 23 run](embench-llvm23-main.md).

#!/bin/sh

variant=$1
shift

etiss_build/bin/bare_etiss_processor -ietiss_riscv_examples/install-$variant/ini/chacha20.ini \
    --vp.stats_file_path=$(pwd)/metrics-$variant.json --etiss.loglevel=1 \
    --arch.cpu=RV32IXCHACHA $@ | awk '/=== Simulation start ===/ {found=1} found && /=== Simulation end ===/ {print; exit} found'

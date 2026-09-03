#!/bin/sh

echo -n "$2 code size (O3): " 
$1/bin/riscv32-unknown-elf-nm etiss_riscv_examples/install-$2-o3/bin/chacha20 \
    -t dec -S | grep -i " t " | grep "double_rounds" | awk '{sum+=$2;} END{print sum;}' | numfmt --to=si
echo -n "$2 code size (Os): " 
$1/bin/riscv32-unknown-elf-nm etiss_riscv_examples/install-$2-os/bin/chacha20 \
    -t dec -S | grep -i " t " | grep "double_rounds" | awk '{sum+=$2;} END{print sum;}' | numfmt --to=si

#!/bin/sh

echo -n "$1 cycle count (O3): "
jq -r '.CPU_cycle' metrics-$1-o3.json | awk '{print $1 + 0}' | numfmt --to=si
echo -n "$1 cycle count (Os): "
jq -r '.CPU_cycle' metrics-$1-os.json | awk '{print $1 + 0}' | numfmt --to=si

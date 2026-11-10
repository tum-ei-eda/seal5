#!/bin/bash

set -e

on_error() {
    echo "building $2 failed" >&2
    exit $1
}

trap 'on_error $? $4' ERR

PATH=$2:$PATH
test -d etiss_riscv_examples/build-$4 && rm -rf etiss_riscv_examples/build-$4
mkdir -p etiss_riscv_examples/build-$4
cd etiss_riscv_examples/build-$4
cmake -DCMAKE_TOOLCHAIN_FILE=$3 -DRISCV_TOOLCHAIN_PREFIX=$1 \
    -DCMAKE_BUILD_TYPE=Release -DCMAKE_C_FLAGS_RELEASE="-g -$5" -DCMAKE_CXX_FLAGS_RELEASE="-g -$5" \
    -DCMAKE_INSTALL_PREFIX=../install-$4 .. &> ../$4.log
make -j4 chacha20 install &>> ../$4.log

echo "finished building $4"

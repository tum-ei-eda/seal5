#!/bin/bash

set -e
#Use this if no commands found: export PYTHONPATH=$(pwd):$PYTHONPATH

Example_files=examples/cdsl/rv_example/Example.core_desc
SEAL5_HOME=/tmp/var/seal5_demo
SEAL5_SRC=~/Desktop/seal5
Config_files=(examples/cfg/llvm.yml examples/cfg/filter.yml examples/cfg/patches.yml examples/cfg/riscv.yml examples/cfg/tests.yml examples/cfg/passes.yml examples/cfg/git.yml)

echo Example_files:;
echo ${Example_files};
echo Config_files:;
echo ${Config_files[@]};
echo Seal5 Build Home:;
echo ${SEAL5_HOME};


seal5 --verbose --dir $SEAL5_HOME reset  --settings;
seal5 --verbose --dir $SEAL5_HOME clean --temp --patches --models --inputs;
seal5 --verbose --dir $SEAL5_HOME init --non-interactive;
seal5 --verbose load --files ${Example_files};
seal5 --verbose load --files ${Config_files[@]};
seal5 --verbose setup;
seal5 --verbose patch -s 0;
seal5 --verbose build;
seal5 --verbose transform;
seal5 --verbose generate --skip patter_gen;
seal5 --verbose patch -s 1 2;
seal5 --verbose build;
seal5 --verbose build -t pattern-gen;
seal5 --verbose build -t llc;
seal5 --verbose generate --only patter_gen;
seal5 --verbose patch -s 3 4 5;
seal5 --verbose build;
seal5 --verbose test;
seal5 --verbose deploy;
seal5 --verbose export;
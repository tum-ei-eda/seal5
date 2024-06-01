#!/bin/bash

set -e
#Use this if no commands found: export PYTHONPATH=$(pwd):$PYTHONPATH

Example_files=examples/cdsl/rv_example/Example.core_desc
Config_files=examples/cfg/*.yml

echo ${Config_files};

seal5 reset --verbose --settings;
seal5 clean --temp --patches --models --inputs --verbose;
seal5 init --verbose;
seal5 load --files ${Example_files};
seal5 load --files ${Config_files};
seal5 setup --verbose;
seal5 patch -s 0 --verbose;
seal5 build  --verbose;
seal5 transform --verbose;
seal5 generate --skip patter_gen --verbose;
seal5 patch -s 1 2 --verbose;
seal5 build  --verbose;
seal5 build  --verbose -t pattern-gen;
seal5 build  --verbose -t llc;
seal5 generate --only patter_gen --verbose;
seal5 patch -s 3 4 5 --verbose;
seal5 build --verbose;
seal5 test --verbose;
seal5 deploy --verbose;
seal5 export --verbose;
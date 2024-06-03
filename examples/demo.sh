#!/bin/bash

set -e
#Use this if no commands found: export PYTHONPATH=$(pwd):$PYTHONPATH

Example_files=examples/cdsl/rv_example/Example.core_desc
Config_files=examples/cfg/*.yml
DEST=${DEST:-/tmp/var/seal5_demo}

Config_files=examples/cfg/*.yml

echo Config_files:;
echo ${Config_files};
echo Example_files:;
echo ${Example_files};
echo Build destination:;
echo ${DEST};

seal5 reset --verbose --settings -dir DEST;
seal5 clean --temp --patches --models --inputs --verbose -dir DEST;
seal5 init --verbose -dir DEST;
seal5 load --files ${Example_files} -dir DEST;
seal5 load --files ${Config_files} -dir DEST;
seal5 setup --verbose -dir DEST;
seal5 patch -s 0 --verbose -dir DEST;
seal5 build  --verbose -dir DEST;
seal5 transform --verbose -dir DEST;
seal5 generate --skip patter_gen --verbose -dir DEST;
seal5 patch -s 1 2 --verbose -dir DEST;
seal5 build  --verbose -dir DEST;
seal5 build  --verbose -t pattern-gen -dir DEST;
seal5 build  --verbose -t llc -dir DEST;
seal5 generate --only patter_gen --verbose -dir DEST;
seal5 patch -s 3 4 5 --verbose -dir DEST;
seal5 build --verbose -dir DEST;
seal5 test --verbose -dir DEST;
seal5 deploy --verbose -dir DEST;
seal5 export --verbose -dir DEST;
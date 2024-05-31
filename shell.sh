#!/bin/bash

set -e
#export PYTHONPATH=$(pwd):$PYTHONPATH

Example_files=examples/cdsl/rv_example/Example.core_desc
Config_files=examples/cfg/*.yml

echo ${Config_files};

seal5 reset --verbose --settings;
seal5 clean --temp --patches --models --inputs --verbose;
seal5 init --verbose;
seal5 load --files ${Example_files};
seal5 load --files ${Config_files};
seal5 setup --verbose;

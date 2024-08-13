#!/bin/bash
#
# Copyright (c) 2024 Kappes Johannes.
#
# This file is part of Seal5.
# See https://github.com/tum-ei-eda/seal5.git for further info.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#


set -e
#Use this if no commands found: export PYTHONPATH=$(pwd):$PYTHONPATH

Example_files=examples/cdsl/rv_example/Example.core_desc
SEAL5_HOME=/tmp/var/seal5
Config_files=(examples/cfg/llvm.yml examples/cfg/filter.yml examples/cfg/patches.yml examples/cfg/riscv.yml examples/cfg/tests.yml examples/cfg/passes.yml examples/cfg/git.yml)

echo Example_files:;
echo ${Example_files};
echo Config_files:;
echo ${Config_files[@]};
echo Seal5 Build Home:;
echo ${SEAL5_HOME};


seal5 --verbose --dir ${SEAL5_HOME} reset  --settings
seal5 --verbose --dir ${SEAL5_HOME} clean --temp --patches --models --inputs
seal5 --verbose --dir ${SEAL5_HOME} init --non-interactive -c
seal5 --verbose load --files ${Example_files}
seal5 --verbose load --files ${Config_files[@]}
seal5 --verbose setup
seal5 --verbose patch -s 0
seal5 --verbose build
seal5 --verbose transform
seal5 --verbose generate --skip pattern_gen
seal5 --verbose patch -s 1 2
seal5 --verbose build
seal5 --verbose build -t pattern-gen
seal5 --verbose build -t llc
seal5 --verbose generate --only pattern_gen
seal5 --verbose patch -s 3 4 5
seal5 --verbose build
seal5 --verbose test
seal5 --verbose install --dest ${SEAL5_HOME}/seal5_llvm_install.zip
seal5 --verbose deploy --dest ${SEAL5_HOME}/seal5_llvm_source.zip
seal5 --verbose export

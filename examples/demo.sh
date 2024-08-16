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

VERBOSE=${VERBOSE:-0}
SKIP_PATTERNS=${SKIP_PATTERNS:-0}
INTERACTIVE=${INTERACTIVE:-0}
# PREPATCHED=${PREPATCHED:-0}
BUILD_CONFIG=${BUILD_CONFIG:-"release"}
IGNORE_ERROR=${IGNORE_ERRORI:-1}
TEST=${TEST:-1}
INSTALL=${INSTALL:-1}
DEPLOY=${DEPLOY:-1}
EXPORT=${EXPORT:-1}
CLEANUP=${CLEANUP:-0}
PROGRESS=${PROGRESS:-1}
CLONE_DEPTH=${CLONE_DEPTH:-1}
DEST=${DEST:-"/tmp/seal5_llvm_cli_demo"}
NAME=${NAME:-"cli_demo"}

Example_files=examples/cdsl/rv_example/Example.core_desc
export SEAL5_HOME=$DEST
Config_files=(examples/cfg/llvm.yml examples/cfg/filter.yml examples/cfg/patches.yml examples/cfg/riscv.yml examples/cfg/tests.yml examples/cfg/passes.yml examples/cfg/git.yml)

echo Example_files:;
echo ${Example_files};
echo Config_files:;
echo ${Config_files[@]};
echo Seal5 Build Home:;
echo ${SEAL5_HOME};

PROGRESS_ARGS=""
if [[ $PROGRESS -eq 1 ]]
then
    PROGRESS_ARGS="--progress"
fi

INTERACTIVE_ARGS=""
if [[ $INTERACTIVE -eq 0 ]]
then
    PROGRESS_ARGS="--non-interactive"
fi


seal5 --verbose --dir ${SEAL5_HOME} reset  --settings
seal5 --verbose --dir ${SEAL5_HOME} clean --temp --patches --models --inputs
seal5 --verbose --dir ${SEAL5_HOME} init $INTERACTIVE_ARGS -c --clone-depth $CLONE_DEPTH $PROGRESS_ARGS
seal5 --verbose load --files ${Example_files}
seal5 --verbose load --files ${Config_files[@]}
seal5 --verbose setup $PROGRESS_ARGS
seal5 --verbose patch -s 0
seal5 --verbose build --config $BUILD_CONFIG
seal5 --verbose transform
seal5 --verbose generate --skip pattern_gen
seal5 --verbose patch -s 1 2
if [[ $SKIP_PATTERNS -eq 0 ]]
then
    seal5 --verbose build --config $BUILD_CONFIG
    seal5 --verbose build --config $BUILD_CONFIG -t pattern-gen
    seal5 --verbose build --config $BUILD_CONFIG -t llc
    seal5 --verbose generate --only pattern_gen
fi
seal5 --verbose patch -s 3 4 5
seal5 --verbose build --config $BUILD_CONFIG

if [[ $TEST -eq 1 ]]
then
    TEST_EXTRA_ARGS=""
    if [[ $IGNORE_ERROR -eq 1 ]]
    then
        TEST_EXTRA_ARGS="$TEST_EXTRA_ARGS --ignore-error"
    fi
    seal5 --verbose test
fi

if [[ $INSTALL -eq 1 ]]
then
    seal5 --verbose install
fi

if [[ $DEPLOY -eq 1 ]]
then
    seal5 --verbose deploy --dest ${DEST%/}_source.zip
fi

if [[ $EXPORT -eq 1 ]]
then
    seal5 --verbose export --dest ${DEST%/}.tar.gz
fi

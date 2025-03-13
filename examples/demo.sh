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

# export VERBOSE=${VERBOSE:-0}
# export SKIP_PATTERNS=${SKIP_PATTERNS:-0}
# export INTERACTIVE=${INTERACTIVE:-0}
# export # PREPATCHED=${PREPATCHED:-0}
# export BUILD_CONFIG=${BUILD_CONFIG:-"release"}
# export IGNORE_ERROR=${IGNORE_ERROR:-1}
# export TEST=${TEST:-1}
# export INSTALL=${INSTALL:-1}
# export DEPLOY=${DEPLOY:-1}
# export EXPORT=${EXPORT:-1}
# export CLEANUP=${CLEANUP:-0}
# export PROGRESS=${PROGRESS:-1}
# export CCACHE=${PROGRESS:-0}
# export CLONE_DEPTH=${CLONE_DEPTH:-1}
export DEST=${DEST:-"/tmp/seal5_llvm_cli_demo"}
# export NAME=${NAME:-"cli_demo"}

Example_files=examples/example/cdsl/Example.core_desc
export SEAL5_HOME=$DEST
Config_files=(examples/common/cfg/llvm.yml examples/common/cfg/filter.yml examples/common/cfg/patches.yml examples/common/cfg/riscv.yml examples/common/cfg/tests.yml examples/common/cfg/passes.yml examples/common/cfg/git.yml)
Test_files=(examples/example/tests/xexample-*.s examples/example/tests/xexample-*.ll examples/example/tests/xexample-*.c)

seal5 --verbose --dir ${SEAL5_HOME} wrapper ${Example_files} ${Config_files[@]} ${Test_files[@]}

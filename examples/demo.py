#
# Copyright (c) 2023 TUM Department of Electrical and Computer Engineering.
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
"""Demo script for Seal5 Python API."""
import os

# import logging
from pathlib import Path

from seal5.flow import Seal5Flow
from seal5.logging import set_log_level
from seal5.types import PatchStage

# set_log_level(console_level=logging.DEBUG, file_level=logging.DEBUG)
set_log_level(console_level="DEBUG", file_level="DEBUG")

EXAMPLES_DIR = Path(os.path.dirname(os.path.realpath(__file__)))
VERBOSE = False
# VERBOSE = True


seal5_flow = Seal5Flow("/tmp/seal5_llvm_demo", "demo")

# Clone LLVM and init seal5 metadata directory
seal5_flow.initialize(
    clone=True,
    clone_url="https://github.com/llvm/llvm-project.git",
    clone_ref="llvmorg-17.0.6",
    force=True,
    verbose=VERBOSE,
)

# Clone Seal5 dependencies
# 1. M2-ISA-R (frontend only)
# 2. CDSL2LLVM (later)
# seal5_flow.setup(force=True, verbose=VERBOSE)

# Load CoreDSL inputs
cdsl_files = [
    EXAMPLES_DIR / "cdsl" / "rv_xcorev" / "XCoreVMac.core_desc",
    EXAMPLES_DIR / "cdsl" / "rv_xcorev" / "XCoreVAlu.core_desc",
    EXAMPLES_DIR / "cdsl" / "rv_xcorev" / "XCoreVMem.core_desc",
    EXAMPLES_DIR / "cdsl" / "rv_xcorev" / "XCoreVBranchImmediate.core_desc"
]
seal5_flow.load(cdsl_files, verbose=VERBOSE, overwrite=True)

# Load YAML inputs
cfg_files = [
    EXAMPLES_DIR / "cfg" / "XCoreVMac.yml",
    EXAMPLES_DIR / "cfg" / "XCoreVAlu.yml",
    EXAMPLES_DIR / "cfg" / "XCoreVMem.yml",
    EXAMPLES_DIR / "cfg" / "XCoreVBranchImmediate.yml",
    EXAMPLES_DIR / "cfg" / "llvm.yml",
    EXAMPLES_DIR / "cfg" / "filter.yml",
    EXAMPLES_DIR / "cfg" / "patches.yml",
    EXAMPLES_DIR / "cfg" / "git.yml",
]
seal5_flow.load(cfg_files, verbose=VERBOSE, overwrite=False)

# Apply initial patches
seal5_flow.patch(verbose=VERBOSE, stages=[PatchStage.PHASE_0])

# Build initial LLVM
# seal5_flow.build(verbose=VERBOSE, config="release")


# Transform inputs
#   1. Create M2-ISA-R metamodel
#   2. Convert to Seal5 metamodel (including aliases, builtins,...)
#   3. Analyse/optimize instructions
seal5_flow.transform(verbose=VERBOSE)

# Generate patches
seal5_flow.generate(verbose=VERBOSE)

# Apply patches
seal5_flow.patch(verbose=VERBOSE)

# Build patched LLVM
seal5_flow.build(verbose=VERBOSE, config="release")

# Test patched LLVM
seal5_flow.test(verbose=VERBOSE, ignore_error=True)

# Deploy patched LLVM (combine commits and create tag)
seal5_flow.deploy(verbose=VERBOSE)

# Export patches, logs, reports
seal5_flow.export("/tmp/seal5_llvm_demo.tar.gz", verbose=VERBOSE)

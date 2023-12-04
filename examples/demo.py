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
from seal5.flow import Seal5Flow

EXAMPLES_DIR = None

seal5_flow = Seal5Flow("/tmp/seal5_llvm_demo", "demo")

# Clone LLVM and init seal5 metadata directory
seal5_flow.initialize(
    clone=True,
    clone_url="TODO",
    clone_ref="TODO",
    force=True,
)

# Clone Seal5 dependencies
# 1. M2-ISA-R (frontend only)
# 2. CDSL2LLVM (later)
seal5_flow.setup()

# Load CoreDSL inputs
# XCVMac.core_desc
seal5_flow.load()

# Load YAML inputs
# XCVMac.yml
# llvm.yml
seal5_flow.load()

# Build initial LLVM
seal5_flow.build()

# Transform inputs
#   1. Create M2-ISA-R metamodel
#   2. Convert to Seal5 metamodel (including aliases, builtins,...)
#   3. Analyse/optimize instructions
seal5_flow.transform()

# Generate patches
seal5_flow.generate()

# Apply patches
seal5_flow.patch()

# Build patched LLVM
seal5_flow.build()

# Test patched LLVM
seal5_flow.test()

# Deploy patched LLVM (combine commits and create tag)
seal5_flow.deploy()

# Export patches, logs, reports
seal5_flow.export("/tmp/seal5_llvm_demo.tar.gz")

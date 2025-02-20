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
"""Demo script for the Seal5 Flow."""
import os

# import logging
from pathlib import Path

from seal5.wrapper import run_seal5_flow
from seal5.logging import set_log_level

# set_log_level(console_level=logging.DEBUG, file_level=logging.DEBUG)
set_log_level(console_level="DEBUG", file_level="DEBUG")

EXAMPLES_DIR = Path(os.path.dirname(os.path.realpath(__file__)))
DEST_DIR = os.environ.get("DEST_DIR", "/tmp")
DEST = os.environ.get("DEST", DEST_DIR + "/seal5_llvm_corev").rstrip("/")

FILES = [
    # CoreDSL inputs
    EXAMPLES_DIR / "cdsl" / "rv_xcorev" / "XCoreVMac.core_desc",
    EXAMPLES_DIR / "cdsl" / "rv_xcorev" / "XCoreVAlu.core_desc",
    EXAMPLES_DIR / "cdsl" / "rv_xcorev" / "XCoreVBitmanip.core_desc",
    EXAMPLES_DIR / "cdsl" / "rv_xcorev" / "XCoreVSimd.core_desc",
    EXAMPLES_DIR / "cdsl" / "rv_xcorev" / "XCoreVMem.core_desc",
    # EXAMPLES_DIR / "cdsl" / "rv_xcorev" / "XCoreVBranchImmediate.core_desc",

    # Test inputs
    EXAMPLES_DIR / "tests" / "xcorev" / "alu" / "*.c",
    EXAMPLES_DIR / "tests" / "xcorev" / "alu" / "*.s",
    EXAMPLES_DIR / "tests" / "xcorev" / "alu" / "*.ll",
    EXAMPLES_DIR / "tests" / "xcorev" / "mac" / "*.c",
    EXAMPLES_DIR / "tests" / "xcorev" / "mac" / "*.s",
    EXAMPLES_DIR / "tests" / "xcorev" / "mac" / "*.ll",
    EXAMPLES_DIR / "tests" / "xcorev" / "bitmanip" / "*.s",
    EXAMPLES_DIR / "tests" / "xcorev" / "bitmanip" / "*.ll",
    # EXAMPLES_DIR / "tests" / "xcorev" / "bi" / "*.s",
    # EXAMPLES_DIR / "tests" / "xcorev" / "bi" / "*.ll",
    # EXAMPLES_DIR / "tests" / "xcorev" / "simd" / "*.s",
    # EXAMPLES_DIR / "tests" / "xcorev" / "simd" / "*.ll",
    # EXAMPLES_DIR / "tests" / "xcorev" / "mem" / "*.s",
    # EXAMPLES_DIR / "tests" / "xcorev" / "mem" / "*.ll",

    # YAML inputs
    EXAMPLES_DIR / "cfg" / "xcorev" / "XCoreVMac.yml",
    EXAMPLES_DIR / "cfg" / "xcorev" / "XCoreVAlu.yml",
    EXAMPLES_DIR / "cfg" / "xcorev" / "XCoreVBitmanip.yml",
    EXAMPLES_DIR / "cfg" / "xcorev" / "XCoreVSimd.yml",
    EXAMPLES_DIR / "cfg" / "xcorev" / "XCoreVMem.yml",
    EXAMPLES_DIR / "cfg" / "xcorev" / "filter.yml",
    EXAMPLES_DIR / "cfg" / "xcorev" / "riscv.yml",
    EXAMPLES_DIR / "cfg" / "llvm.yml",
    EXAMPLES_DIR / "cfg" / "patches.yml",
    EXAMPLES_DIR / "cfg" / "tests.yml",
    EXAMPLES_DIR / "cfg" / "passes.yml",
    EXAMPLES_DIR / "cfg" / "git.yml",
]
run_seal5_flow(FILES, name="corev", dest=DEST)

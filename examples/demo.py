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
DEST = os.environ.get("DEST", DEST_DIR + "/seal5_llvm_demo").rstrip("/")

FILES = [
    # CoreDSL inputs
    EXAMPLES_DIR / "example" / "cdsl" / "Example.core_desc",
    # Test inputs
    EXAMPLES_DIR / "example" / "tests" / "xexample.*.s",
    EXAMPLES_DIR / "example" / "tests" / "xexample.*.ll",
    EXAMPLES_DIR / "example" / "tests" / "xexample.*.c",
    # YAML inputs
    EXAMPLES_DIR / "common" / "cfg" / "llvm.yml",
    EXAMPLES_DIR / "common" / "cfg" / "filter.yml",
    EXAMPLES_DIR / "common" / "cfg" / "patches.yml",
    EXAMPLES_DIR / "common" / "cfg" / "riscv.yml",
    EXAMPLES_DIR / "common" / "cfg" / "tests.yml",
    EXAMPLES_DIR / "common" / "cfg" / "passes.yml",
    EXAMPLES_DIR / "common" / "cfg" / "git.yml",
    EXAMPLES_DIR / "example" / "cfg" / "intrinsics.yml",
]

run_seal5_flow(FILES, name="demo", dest=DEST)

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

from pathlib import Path

from seal5.wrapper import run_seal5_flow


EXAMPLES_DIR = Path(os.path.dirname(os.path.realpath(__file__)))
DEST_DIR = os.environ.get("DEST_DIR", "/tmp")
DEST = os.environ.get("DEST", DEST_DIR + "/seal5_llvm_openasip").rstrip("/")

FILES = [
    # CoreDSL inputs
    EXAMPLES_DIR / "openasip" / "cdsl" / "OpenASIP_base.core_desc",
    EXAMPLES_DIR / "openasip" / "cdsl" / "OpenASIP_paper.core_desc",
    # Test inputs
    EXAMPLES_DIR / "openasip" / "tests" / "base" / "*.c",
    EXAMPLES_DIR / "openasip" / "tests" / "base" / "*.s",
    EXAMPLES_DIR / "openasip" / "tests" / "base" / "*.ll",
    # EXAMPLES_DIR / "openasip" / "tests" / "base" / "*.mir",
    # YAML inputs
    EXAMPLES_DIR / "openasip" / "cfg" / "OpenASIP_paper.yml",
    EXAMPLES_DIR / "openasip" / "cfg" / "OpenASIP_base.yml",
    EXAMPLES_DIR / "openasip" / "cfg" / "intrinsics.yml",
    EXAMPLES_DIR / "common" / "cfg" / "llvm.yml",
    EXAMPLES_DIR / "common" / "cfg" / "filter.yml",
    EXAMPLES_DIR / "common" / "cfg" / "patches.yml",
    EXAMPLES_DIR / "common" / "cfg" / "tests.yml",
    EXAMPLES_DIR / "common" / "cfg" / "passes.yml",
    EXAMPLES_DIR / "common" / "cfg" / "git.yml",
]
run_seal5_flow(FILES, name="openasip", dest=DEST)

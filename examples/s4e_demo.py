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


DEMO_NAME = os.environ.get("DEMO_NAME", "s4e")
EXAMPLES_DIR = Path(os.path.dirname(os.path.realpath(__file__)))
DEMO_CDSL_DIR = Path(os.environ.get("DEMO_CDSL_DIR", EXAMPLES_DIR / DEMO_NAME / "cdsl"))
DEMO_TESTS_DIR = Path(os.environ.get("DEMO_TESTS_DIR", EXAMPLES_DIR / DEMO_NAME / "tests"))
DEMO_CFG_DIR = Path(os.environ.get("DEMO_CFG_DIR", EXAMPLES_DIR / DEMO_NAME / "cfg"))
COMMON_CFG_DIR = Path(os.environ.get("COMMON_CFG_DIR", EXAMPLES_DIR / "common" / "cfg"))
DEST_DIR = os.environ.get("DEST_DIR", "/tmp")
DEST = os.environ.get("DEST", DEST_DIR + "/seal5_llvm_" + DEMO_NAME).rstrip("/")

FILES = [
    # CoreDSL inputs
    DEMO_CDSL_DIR / "s4e-mac.core_desc",
    # Test inputs
    DEMO_TESTS_DIR / "*.s",
    DEMO_TESTS_DIR / "*.c",
    # DEMO_TESTS_DIR / "*.ll",
    # YAML inputs
    DEMO_CFG_DIR / "s4e-mac.yml",
    COMMON_CFG_DIR / "llvm.yml",
    COMMON_CFG_DIR / "filter.yml",
    COMMON_CFG_DIR / "patches.yml",
    COMMON_CFG_DIR / "riscv.yml",
    COMMON_CFG_DIR / "tests.yml",
    COMMON_CFG_DIR / "passes.yml",
    COMMON_CFG_DIR / "git.yml",
]
run_seal5_flow(FILES, name=DEMO_NAME, dest=DEST)

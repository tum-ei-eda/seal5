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
# VERBOSE = False
VERBOSE = bool(int(os.environ.get("VERBOSE", 0)))
FAST = bool(int(os.environ.get("FAST", 1)))
SKIP_PATTERNS = bool(int(os.environ.get("SKIP_PATTERNS", 0)))
INTERACTIVE = bool(int(os.environ.get("INTERACTIVE", 0)))
PREPATCHED = bool(int(os.environ.get("PREPATCHED", 0)))
BUILD_CONFIG = os.environ.get("BUILD_CONFIG", "release")
DEST = os.environ.get("BUILD_CONFIG", "/tmp/seal5_llvm_gen")
NAME = os.environ.get("NAME", "gen")

seal5_flow = Seal5Flow(DEST, NAME)

# Optional: clean existing settings/models for fresh run
seal5_flow.reset(settings=True, interactive=False)
seal5_flow.clean(temp=True, patches=True, models=True, inputs=True, interactive=INTERACTIVE)

if PREPATCHED:
    if seal5_flow.repo is None or "seal5-gen-stage0" not in seal5_flow.repo.tags:
        raise RuntimeError("PREPATCHED can only be used after LLVM was patched at least once.")

# Clone LLVM and init seal5 metadata directory
seal5_flow.initialize(
    clone=True,
    clone_url="https://github.com/llvm/llvm-project.git",
    # clone_ref="llvmorg-17.0.6",
    clone_ref="seal5-gen-stage0" if PREPATCHED else "llvmorg-18.1.0-rc3",
    force=True,
    verbose=VERBOSE,
)

# Load CoreDSL inputs
cdsl_files = [
    # EXAMPLES_DIR / "cdsl" / "rv_gen" / "all_v7.core_desc",
    EXAMPLES_DIR
    / "cdsl"
    / "rv_gen"
    / "all_v9.core_desc",
]
seal5_flow.load(cdsl_files, verbose=VERBOSE, overwrite=True)

# Load test inputs
test_files = []
seal5_flow.load(test_files, verbose=VERBOSE, overwrite=True)

# Load YAML inputs
cfg_files = [
    # GENERATED
    EXAMPLES_DIR / "cfg" / "gen" / "all.yml",
    EXAMPLES_DIR / "cfg" / "gen" / "riscv.yml",
    EXAMPLES_DIR / "cfg" / "llvm.yml",
    EXAMPLES_DIR / "cfg" / "filter.yml",
    EXAMPLES_DIR / "cfg" / "patches.yml",
    EXAMPLES_DIR / "cfg" / "tests.yml",
    EXAMPLES_DIR / "cfg" / "passes.yml",
    EXAMPLES_DIR / "cfg" / "git.yml",
]
seal5_flow.load(cfg_files, verbose=VERBOSE, overwrite=False)

# Override settings from Python
seal5_flow.settings.llvm.default_config = BUILD_CONFIG

# Clone & install Seal5 dependencies
# 1. CDSL2LLVM (add PHASE_0 patches)
seal5_flow.setup(force=True, verbose=VERBOSE)

# Apply initial patches
if not PREPATCHED:
    seal5_flow.patch(verbose=VERBOSE, stages=[PatchStage.PHASE_0])

if not FAST:
    # Build initial LLVM
    seal5_flow.build(verbose=VERBOSE, config=BUILD_CONFIG)

# Transform inputs
#   1. Create M2-ISA-R metamodel
#   2. Convert to Seal5 metamodel (including aliases, builtins,...)
#   3. Analyse/optimize instructions
seal5_flow.transform(verbose=VERBOSE)

# Generate patches (except Patterns)
seal5_flow.generate(verbose=VERBOSE, skip=["pattern_gen"])

# Apply next patches
seal5_flow.patch(verbose=VERBOSE, stages=[PatchStage.PHASE_1, PatchStage.PHASE_2])

if not FAST:
    # Build patched LLVM
    seal5_flow.build(verbose=VERBOSE, config=BUILD_CONFIG)
if not SKIP_PATTERNS:
    # Build PatternGen & llc
    seal5_flow.build(verbose=VERBOSE, config=BUILD_CONFIG, target="pattern-gen")
    seal5_flow.build(verbose=VERBOSE, config=BUILD_CONFIG, target="llc")

    # Generate remaining patches
    seal5_flow.generate(verbose=VERBOSE, only=["pattern_gen"])

    # Apply patches
    seal5_flow.patch(verbose=VERBOSE, stages=list(range(PatchStage.PHASE_3, PatchStage.PHASE_5 + 1)))

# Build patched LLVM
seal5_flow.build(verbose=VERBOSE, config=BUILD_CONFIG)

# Test patched LLVM
seal5_flow.test(verbose=VERBOSE, ignore_error=True)

# Deploy patched LLVM (combine commits and create tag)
seal5_flow.deploy(verbose=VERBOSE)

# Export patches, logs, reports
seal5_flow.export(f"{DEST}.tar.gz", verbose=VERBOSE)

# Optional: cleanup temorary files, build dirs,...
# seal5.clean(temp=True, build=True, deps=True, interactive=INTERACTIVE)

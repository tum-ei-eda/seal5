#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Even/odd RV32 register pairs, using LLVM 23's GPRPair infrastructure."""
import os
from pathlib import Path

from seal5.wrapper import LLVM_REF, run_seal5_flow

if not LLVM_REF.startswith("llvmorg-23."):
    raise ValueError("The register-pair example requires LLVM_REF=llvmorg-23.*")
EXAMPLES = Path(__file__).resolve().parent
FILES = [
    EXAMPLES / "regpairs/cdsl/RegPairs.core_desc",
    EXAMPLES / "regpairs/tests/*.s",
    EXAMPLES / "regpairs/tests/*.c",
    EXAMPLES / "regpairs/tests/*.ll",
    *[EXAMPLES / "common/cfg" / f"{name}.yml" for name in ("llvm", "filter", "patches", "tests", "passes", "git")],
    EXAMPLES / "regpairs/cfg/regpairs.yml",
]
run_seal5_flow(
    FILES,
    name="regpairs",
    dest=os.environ.get("DEST", "/tmp/seal5_llvm_regpairs"),
    lookup_paths=[EXAMPLES / "common/cdsl/rv_base"],
    skip_patterns=False,
)

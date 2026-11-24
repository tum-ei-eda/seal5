#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Even/odd RV32 register pairs, using LLVM 22/23's GPRPair infrastructure."""
import os
from pathlib import Path

from seal5.wrapper import LLVM_REF, run_seal5_flow

if not LLVM_REF.startswith(("llvmorg-22.", "llvmorg-23.")):
    raise ValueError("The register-pair example requires LLVM_REF=llvmorg-22.* or llvmorg-23.*")
EXAMPLES = Path(__file__).resolve().parent
PAIR_STYLE = os.environ.get("PAIR_STYLE", "explicit")
if PAIR_STYLE not in ("explicit", "inferred"):
    raise ValueError("PAIR_STYLE must be explicit or inferred")
PAIR_SOURCE = "RegPairs.core_desc" if PAIR_STYLE == "explicit" else "inferred/RegPairs.core_desc"
FILES = [
    EXAMPLES / "regpairs/cdsl" / PAIR_SOURCE,
    EXAMPLES / "regpairs/tests/*.s",
    EXAMPLES / "regpairs/tests/*.c",
    EXAMPLES / "regpairs/tests/*.ll",
    *[EXAMPLES / "common/cfg" / f"{name}.yml" for name in ("llvm", "filter", "patches", "tests", "passes", "git")],
    EXAMPLES / "regpairs/cfg/regpairs.yml",
]
if LLVM_REF.startswith("llvmorg-22."):
    FILES.append(EXAMPLES / "regpairs/cfg/llvm22.yml")
run_seal5_flow(
    FILES,
    name="regpairs",
    dest=os.environ.get("DEST", "/tmp/seal5_llvm_regpairs"),
    lookup_paths=[EXAMPLES / "common/cdsl/rv_base"],
    skip_patterns=False,
)

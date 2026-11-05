#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Exercise the ordinary TableGen packed SIMD patterns on LLVM 22 or 23."""

import os
from pathlib import Path

from seal5.wrapper import LLVM_REF, run_seal5_flow

if not LLVM_REF.startswith(("llvmorg-22.", "llvmorg-23.")):
    raise ValueError("The packed SIMD example requires LLVM_REF=llvmorg-22.* or llvmorg-23.*")

EXAMPLES = Path(__file__).resolve().parent
FILES = [
    EXAMPLES / "packed_simd/cdsl/PackedSIMD.core_desc",
    EXAMPLES / "packed_simd/tests/*.ll",
    *[
        EXAMPLES / "common/cfg" / f"{name}.yml"
        for name in ("llvm", "filter", "patches", "riscv", "tests", "passes", "git")
    ],
    EXAMPLES / "packed_simd/cfg/passes.yml",
    EXAMPLES / "packed_simd/cfg" / ("llvm22.yml" if LLVM_REF.startswith("llvmorg-22.") else "llvm23.yml"),
]
run_seal5_flow(
    FILES,
    name="packed_simd_demo",
    dest=os.environ.get("DEST", f"/tmp/seal5_llvm_packed_simd_{LLVM_REF}"),
    lookup_paths=[EXAMPLES / "common/cdsl/rv_base"],
)

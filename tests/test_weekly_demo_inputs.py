# SPDX-License-Identifier: Apache-2.0
"""Exercise weekly demo inputs before starting expensive LLVM builds."""
from pathlib import Path
import subprocess
import sys
from types import SimpleNamespace

import pytest
import yaml

from seal5.backends.riscv_instr_info.writer import gen_intrinsic_pattern
from seal5.settings import ExtensionsSettings, IntrinsicDefn

ROOT = Path(__file__).resolve().parents[1]


@pytest.mark.parametrize(
    "source",
    [
        "example/cdsl/Example64.core_desc",
        "example/cdsl/ExampleRV32C.core_desc",
        "48bit/cdsl/ExampleRV32K.core_desc",
        "openasip/cdsl/OpenASIP_base.core_desc",
        "openasip/cdsl/OpenASIP_paper.core_desc",
        "se/cdsl/insts/out_encoded_etiss.core_desc",
        "tumeda/cdsl/XCoreVNand.core_desc",
    ],
)
def test_weekly_source_parses(source, tmp_path):
    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "seal5.frontends.coredsl",
            str(ROOT / "examples" / source),
            "-o",
            str(tmp_path),
            "--log",
            "warning",
            "--allow-undefined-const",
            "-I",
            str(ROOT / "examples/common/cdsl/rv_base"),
        ],
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, result.stdout + result.stderr
    assert list(tmp_path.glob("*.m2isarmodel"))


def test_nand_intrinsic_matches_source_operands():
    config = yaml.safe_load((ROOT / "examples/tumeda/cfg/intrinsics.yml").read_text())
    intrinsic = IntrinsicDefn.from_dict(config["intrinsics"]["intrinsics"][0])
    instr = SimpleNamespace(
        name="CV_NAND_BITWISE", llvm_intrin_reads=["GPR:$rs1", "GPR:$rs2"], llvm_intrin_ins_str="GPR:$rs1, GPR:$rs2"
    )
    pattern = gen_intrinsic_pattern(instr, "XCoreVNand", intrinsic, ExtensionsSettings(arch="xcorevnand"))
    assert "(OpNode GPR:$rs1, GPR:$rs2)" in pattern

# SPDX-License-Identifier: Apache-2.0
"""Regression coverage for test-generator failures exposed by the LLVM23 demo."""

from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from seal5.tools.cdsl2llvm import run_pattern_gen


class PatternGenTestGenerationTests(unittest.TestCase):
    def generate(self, directory, *, xlen, pattern, immediates):
        root = Path(directory)
        (root / "bin").mkdir()
        (root / "bin" / "pattern-gen").touch()
        source = root / "test.core_desc"
        source.touch()
        destination = root / "test.td"
        destination.touch()
        (root / "test.ll").write_text("define void @implTEST() {\n  ret void\n}\n")
        with patch("seal5.tools.cdsl2llvm.utils.exec_getout", return_value=f"Pattern for TEST [xtest]: {pattern}\n"):
            return run_pattern_gen(root, source, destination, xlen=xlen, mattr="+m", immediate_operands=immediates)

    def test_rv64_result_store(self):
        with tempfile.TemporaryDirectory() as directory:
            files = self.generate(directory, xlen=64, pattern="(add GPR:$lhs, GPR:$rhs)", immediates=[])
            self.assertEqual(len(files), 1)
            contents = Path(files[0]).read_text()
            self.assertIn("RV64-MIR-NEXT: SD", contents)
            self.assertIn("RV64-ASM-NEXT: sd", contents)

    def test_rv32_result_store(self):
        with tempfile.TemporaryDirectory() as directory:
            files = self.generate(directory, xlen=32, pattern="(add GPR:$lhs, GPR:$rhs)", immediates=[])
            contents = Path(files[0]).read_text()
            self.assertIn("RV32-MIR-NEXT: SW", contents)
            self.assertIn("RV32-ASM-NEXT: sw", contents)

    def test_arbitrary_immediate_name_suppresses_runtime_argument_test(self):
        with tempfile.TemporaryDirectory() as directory:
            files = self.generate(directory, xlen=32, pattern="(srl GPR:$lhs, uimm5:$base)", immediates=["base"])
            self.assertEqual(files, [])
            self.assertFalse((Path(directory) / "test.test-cg.ll").exists())


if __name__ == "__main__":
    unittest.main()

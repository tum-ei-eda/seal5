# SPDX-License-Identifier: Apache-2.0
"""Regression coverage for test-generator failures exposed by the LLVM23 demo."""

from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from seal5.tools.cdsl2llvm import combine_test_fragments, run_pattern_gen, scalarize_register_inputs


class PatternGenTestGenerationTests(unittest.TestCase):
    def generate(
        self,
        directory,
        *,
        xlen,
        pattern,
        immediates,
        has_register_output=True,
        may_load=False,
        num_register_outputs=None,
        packed_output=False,
    ):
        root = Path(directory)
        (root / "bin").mkdir()
        (root / "bin" / "pattern-gen").touch()
        source = root / "test.core_desc"
        source.touch()
        destination = root / "test.td"
        ir = "define void @implTEST() {\n  ret void\n}\n"
        if may_load:
            ir = (
                f"define void @implTEST(ptr %base, ptr %rd) {{\n"
                f"  %v = load i{xlen}, ptr %base\n"
                f"  store i{xlen} %v, ptr %rd, align {xlen // 8}\n  ret void\n}}\n"
            )
        (root / "test.ll").write_text(ir)

        def execute(*_args, **_kwargs):
            destination.write_text("(outs GPR32V4:$rd)" if packed_output else "")
            return f"Pattern for TEST [xtest]: {pattern}\n"

        with patch("seal5.tools.cdsl2llvm.utils.exec_getout", side_effect=execute):
            return run_pattern_gen(
                root,
                source,
                destination,
                xlen=xlen,
                mattr="+m",
                immediate_operands=immediates,
                has_register_output=has_register_output,
                may_load=may_load,
                num_register_outputs=num_register_outputs,
            )

    def test_scalar_register_inputs_preserve_subregister_extraction(self):
        ir = (
            "define void @implTEST(ptr noalias writeonly %rd, ptr readonly align 4 %rs1) {\n"
            "  %hi = getelementptr i8, ptr %rs1, i32 2\n"
            "  %v = load i16, ptr %hi\n"
            "  %w = sext i16 %v to i32\n"
            "  store i32 %w, ptr %rd\n  ret void\n}\n"
        )
        with patch("seal5.tools.cdsl2llvm.subprocess.run") as optimize:
            optimize.return_value.stdout = "optimized"
            self.assertEqual(scalarize_register_inputs(ir, 32, Path("/tools/opt")), "optimized")
            args, kwargs = optimize.call_args
            self.assertIn("-passes=sroa,instcombine", args[0])
            prepared = kwargs["input"]
            self.assertIn("ptr noalias writeonly %rd, i32 %rs1.seal5_value", prepared)
            self.assertIn("%rs1 = alloca i32, align 4", prepared)
            self.assertIn("store i32 %rs1.seal5_value, ptr %rs1", prepared)
            self.assertIn("%hi = getelementptr i8, ptr %rs1, i32 2", prepared)
            self.assertIn("store i32 %w, ptr %rd", prepared)

    def test_unrolled_functions_use_distinct_labels_and_the_real_target(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "bin").mkdir()
            (root / "bin/pattern-gen").touch()
            source = root / "test.core_desc"
            source.touch()
            destination = root / "test.td"
            source.with_suffix(".ll").write_text(
                "define void @implTEST_0() {\n  ret void\n}\n" "define void @implTEST_1() {\n  ret void\n}\n"
            )

            def execute(*_args, **_kwargs):
                destination.write_text("def TEST_ : RVInst_TEST<(outs GPR:$rd), (ins GPR:$a)>;\n")
                return (
                    "Pattern for TEST_0 [xtest]: (mul GPR:$a, GPR:$b)\n"
                    "Pattern for TEST_1 [xtest]: (sra (mul GPR:$a, GPR:$b), 1)\n"
                    "source.core_desc: warning: example diagnostic\n"
                    "=== Statistics Collected ===\n1 pattern-gen - Generated patterns\n"
                )

            with patch("seal5.tools.cdsl2llvm.utils.exec_getout", side_effect=execute):
                files = run_pattern_gen(root, source, destination, xlen=32, mattr="+m", immediate_operands=["shift"])
            contents = Path(files[0]).read_text()
            for suffix in [0, 1]:
                self.assertEqual(contents.count(f"RV32-MIR-LABEL: name: implTEST_{suffix}\n"), 1)
                self.assertEqual(contents.count(f"RV32-ASM-LABEL: implTEST_{suffix}:\n"), 1)
            self.assertEqual(contents.count("RV32-MIR: {{^ *[^;]*}} TEST_{{[ ,]}}\n"), 2)
            self.assertNotIn("RV32-MIR: TEST_0\n", contents)
            patterns = Path(str(destination) + ".pat").read_text()
            self.assertNotIn("diagnostic", patterns)
            self.assertNotIn("Statistics", patterns)

    def test_packed_result_allows_register_class_copy(self):
        with tempfile.TemporaryDirectory() as directory:
            files = self.generate(
                directory, xlen=32, pattern="(add GPR32V4:$a, GPR32V4:$b)", immediates=[], packed_output=True
            )
            contents = Path(files[0]).read_text()
            self.assertIn("RV32-MIR: SW", contents)
            self.assertNotIn("RV32-MIR-NEXT: SW", contents)
            self.assertIn("RV32-ASM-NEXT: sw", contents)

    def test_store_has_no_register_result_writeback(self):
        with tempfile.TemporaryDirectory() as directory:
            files = self.generate(
                directory,
                xlen=32,
                pattern="(store GPR:$value, GPR:$address)",
                immediates=[],
                has_register_output=False,
            )
            contents = Path(files[0]).read_text()
            self.assertIn("RV32-MIR: {{^ *[^;]*}} TEST{{[ ,]}}\n  ; RV32-MIR-NEXT: PseudoRET", contents)
            self.assertIn("RV32-ASM: xtest\n  ; RV32-ASM-NEXT: ret", contents)
            self.assertNotIn("RV32-MIR-NEXT: SW", contents)

    def test_load_returns_value_without_competing_store_pattern(self):
        with tempfile.TemporaryDirectory() as directory:
            files = self.generate(
                directory,
                xlen=64,
                pattern="(load GPR:$address)",
                immediates=[],
                may_load=True,
            )
            contents = Path(files[0]).read_text()
            self.assertIn("define i64 @implTEST", contents)
            self.assertIn("ret i64 %v", contents)
            self.assertNotIn("store i64", contents)
            self.assertNotIn("RV64-MIR: SD", contents)
            self.assertNotIn("RV64-ASM: sd", contents)

    def test_register_wrapper_defers_both_writebacks(self):
        with tempfile.TemporaryDirectory() as directory:
            source = Path(directory) / "wrapper.ll"
            source.write_text(
                "define void @implTEST(ptr noalias writeonly initializes((0, 4)) %rd1, "
                "ptr noalias %rd2, i32 %a, i32 %b) {\n"
                "  %sum = add i32 %a, %b\n"
                "  store i32 %sum, ptr %rd1\n"
                "  %diff = sub i32 %a, %b\n"
                "  store i32 %diff, ptr %rd2\n"
                "  ret void\n}\n"
            )
            result = combine_test_fragments(source, "TEST", "", "", "", register_writebacks=2)
            self.assertLess(result.index("%diff = sub"), result.index("store i32 %sum"))
            self.assertEqual(result.count("store i32"), 2)
            source.write_text(source.read_text().replace("ptr noalias %rd2", "ptr %rd2"))
            with self.assertRaisesRegex(AssertionError, "noalias"):
                combine_test_fragments(source, "TEST", "", "", "", register_writebacks=2)

    def test_two_result_writebacks(self):
        for width, opcode in ((32, "SW"), (64, "SD")):
            with self.subTest(width=width), tempfile.TemporaryDirectory() as directory:
                files = self.generate(
                    directory,
                    xlen=width,
                    pattern="(add GPR:$lhs, GPR:$rhs)",
                    immediates=[],
                    num_register_outputs=2,
                )
                contents = Path(files[0]).read_text()
                self.assertEqual(contents.count(f"RV{width}-MIR-NEXT: {opcode}"), 2)
                self.assertEqual(contents.count(f"RV{width}-ASM-NEXT: {opcode.lower()}"), 2)

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

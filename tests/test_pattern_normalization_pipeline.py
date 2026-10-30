# SPDX-License-Identifier: Apache-2.0
"""Exercise source parsing, saved models and the split CoreDSL writer."""

from pathlib import Path
import subprocess
import sys
import tempfile
import unittest


class PipelineTests(unittest.TestCase):
    def test_bformat_displacement_keeps_byte_offsets(self):
        from seal5.model_utils import load_model
        from seal5.backends.riscv_instr_info.writer import gen_riscv_instr_info_str
        from types import SimpleNamespace

        fixture = Path(__file__).parent / "fixtures" / "pattern_normalization.core_desc"
        source = fixture.read_text().replace(
            "rs1[4:0] :: rs2[4:0] :: imm[12:0] :: 9'b11",
            "imm[12:12] :: imm[10:5] :: rs2[4:0] :: rs1[4:0] :: 3'b010 :: imm[4:1] :: imm[11:11] :: 7'b0101011",
        )
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory)
            path = output / "branch.core_desc"
            path.write_text(source)

            def run(module, *args):
                result = subprocess.run([sys.executable, "-m", module, *map(str, args)], text=True, capture_output=True)
                self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

            run("m2isar.frontends.coredsl2_set.parser", path, "-o", output, "--log", "warning")
            run("seal5.transform.converter", output / "branch.m2isarmodel", "--log", "warning")
            model = output / "branch.seal5model"
            for module in (
                "collect_register_operands.collect",
                "collect_immediate_operands.collect",
                "collect_operand_types.collect",
                "detect_inouts.collect",
            ):
                run("seal5.transform." + module, model, "--log", "warning")
            loaded = load_model(model)
            set_def = next(iter(loaded.sets.values()))
            instr = next(i for i in set_def.instructions.values() if i.name == "BRANCH")
            self.assertTrue(instr.is_bformat_branch_offset("imm"))
            self.assertFalse(instr.is_bformat_branch_offset("rs1"))
            self.assertIn("patterngen_btarget:$imm", instr.llvm_ins_str)
            set_def.settings = SimpleNamespace(get_decoder_namespace=lambda **_: "Test")
            generated = gen_riscv_instr_info_str(instr, set_def)
            self.assertIn("bits<13> imm;", generated)
            self.assertIn("Inst{31} = imm{12};", generated)
            self.assertIn("Inst{11-8} = imm{4-1};", generated)
            self.assertIn("InstFormat Format = InstFormatB;", generated)
            from m2isar.metamodel import behav
            from seal5.transform.detect_branches import detect_branch, statements

            assignment = statements(statements(instr.operation).stmts[0])
            assignment.expr = behav.SliceOperation(assignment.expr, behav.Literal(63), behav.Literal(0))
            self.assertEqual(detect_branch(instr.operation, instr.operands)[1], "imm")
            assignment.expr.left = behav.Literal(62)
            self.assertIsNone(detect_branch(instr.operation, instr.operands)[1])

    def test_array_source_to_cdsl(self):
        fixture = Path(__file__).parent / "fixtures" / "array_normalization.core_desc"
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory)

            def run(module, *args):
                result = subprocess.run([sys.executable, "-m", module, *map(str, args)], text=True, capture_output=True)
                self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
                return result.stdout

            run("seal5.frontends.coredsl", fixture, "-o", output, "--log", "warning")
            run("seal5.transform.converter", output / "array_normalization.m2isarmodel", "--log", "warning")
            model = output / "array_normalization.seal5model"
            # Exercise the pipeline handler and model-level configuration merge.
            from types import SimpleNamespace
            from seal5 import pass_list

            settings = SimpleNamespace(
                models_dir=output,
                passes=SimpleNamespace(overrides={"explicit_memory_names": {"enabled": False}}),
                models={
                    "array_normalization": SimpleNamespace(
                        passes=SimpleNamespace(overrides={"explicit_memory_names": {"enabled": True}})
                    )
                },
            )
            pass_list.normalize_subscripts("array_normalization", settings=settings, enabled=True)
            run("seal5.transform.collect_register_operands.collect", model, "--log", "warning")
            run("seal5.transform.collect_immediate_operands.collect", model, "--log", "warning")
            split = output / "split"
            split.mkdir()
            run("seal5.backends.coredsl2.writer", model, "--reduced", "--splitted", "-o", split)
            files = split / "ArrayNormalization"
            load_be = (files / "LOAD_BE.core_desc").read_text()
            store_be = (files / "STORE_BE.core_desc").read_text()
            load_le = (files / "LOAD24_LE.core_desc").read_text()
            self.assertEqual(load_be.count("MEM8["), 4)
            self.assertEqual(store_be.count("MEM8["), 4)
            self.assertEqual(load_le.count("MEM8["), 3)
            self.assertNotIn("MEM[", load_be + store_be + load_le)
            self.assertIn("_seal5_range_value_", store_be)
            self.assertIn("_seal5_range_address_", store_be)

    def test_frontend_rejects_invalid_builtin_uses(self):
        source = (Path(__file__).parent / "fixtures" / "manual_pattern_names.core_desc").read_text()
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory)
            for text, expected in (
                (source.replace("XLEN = 64", "XLEN = 32"), "XW"),
                (source.replace("branch(X[rs1] & X[rs2])", "branch()"), "exactly one"),
                (source.replace("MEMX", "MEMTYPO"), "MEMTYPO"),
            ):
                fixture = output / "invalid.core_desc"
                fixture.write_text(text)
                result = subprocess.run(
                    [sys.executable, "-m", "seal5.frontends.coredsl", str(fixture), "-o", str(output)],
                    text=True,
                    capture_output=True,
                )
                self.assertNotEqual(result.returncode, 0)
                self.assertIn(expected, result.stdout + result.stderr)

    def test_manual_names_survive_transforms(self):
        fixture = Path(__file__).parent / "fixtures" / "manual_pattern_names.core_desc"
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory)

            def run(module, *args):
                result = subprocess.run([sys.executable, "-m", module, *map(str, args)], text=True, capture_output=True)
                self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
                return result.stdout

            run("seal5.frontends.coredsl", fixture, "-o", output, "--log", "warning")
            run("seal5.transform.converter", output / "manual_pattern_names.m2isarmodel", "--log", "warning")
            model = output / "manual_pattern_names.seal5model"
            run("seal5.transform.collect_register_operands.collect", model, "--log", "warning")
            run("seal5.transform.collect_immediate_operands.collect", model, "--log", "warning")
            normalized = output / "normalized.seal5model"
            counts = run(
                "seal5.transform.pattern_normalization",
                model,
                "-o",
                normalized,
                "--explicit-memory-names",
                "--explicit-register-names",
                "--normalize-subscripts",
                "--detect-branches",
            )
            for name in ("memory", "registers", "subscripts", "branches"):
                self.assertIn(f"'{name}': 0", counts)
            rendered = output / "manual.core_desc"
            run("seal5.backends.coredsl2.writer", normalized, "--reduced", "-o", rendered)
            text = rendered.read_text()
            for expected in ("MEMX[X[rs1]]", "MEM16[X[rs1]]", "XW[rs2]", "branch((X[rs1]) & (X[rs2]))"):
                self.assertIn(expected, text)

    def test_source_to_split_cdsl(self):
        fixture = Path(__file__).parent / "fixtures" / "pattern_normalization.core_desc"
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory)

            def run(module, *args):
                result = subprocess.run([sys.executable, "-m", module, *map(str, args)], text=True, capture_output=True)
                self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
                return result.stdout

            run("m2isar.frontends.coredsl2_set.parser", fixture, "-o", output, "--log", "warning")
            run("seal5.transform.converter", output / "pattern_normalization.m2isarmodel", "--log", "warning")
            model = output / "pattern_normalization.seal5model"
            run("seal5.transform.collect_register_operands.collect", model, "--log", "warning")
            run("seal5.transform.collect_immediate_operands.collect", model, "--log", "warning")
            normalized = output / "normalized.seal5model"
            counts = run(
                "seal5.transform.pattern_normalization",
                model,
                "-o",
                normalized,
                "--explicit-memory-names",
                "--explicit-register-names",
                "--normalize-subscripts",
                "--detect-branches",
            )
            for name in ("memory", "registers", "subscripts", "branches"):
                self.assertIn(f"'{name}': 1", counts)
            split = output / "split"
            split.mkdir()
            run("seal5.backends.coredsl2.writer", normalized, "--reduced", "--splitted", "-o", split)
            files = split / "Normalization"
            self.assertIn("MEM32[addr]", (files / "LOAD.core_desc").read_text())
            self.assertIn("XW[rs1]", (files / "WORD.core_desc").read_text())
            self.assertIn("[base +: 5]", (files / "SLICE.core_desc").read_text())
            branch = (files / "BRANCH.core_desc").read_text()
            self.assertIn("branch((X[rs1]) == (X[rs2]))", branch)
            self.assertIn("[[is_branch_offs]]", branch)


if __name__ == "__main__":
    unittest.main()

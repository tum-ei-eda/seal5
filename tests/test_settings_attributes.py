# SPDX-License-Identifier: Apache-2.0
"""Exercise source-level filtering and extension settings."""

from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
import yaml

from seal5.model import Seal5InstrAttribute, Seal5InstSetAttribute
from seal5.model_utils import load_model

FIXTURE = Path(__file__).parent / "fixtures" / "array_normalization.core_desc"


class SettingsAttributeTests(unittest.TestCase):
    def run_module(self, module, *args, success=True):
        result = subprocess.run([sys.executable, "-m", module, *map(str, args)], text=True, capture_output=True)
        if success:
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        else:
            self.assertNotEqual(result.returncode, 0)
        return result.stdout + result.stderr

    def parse(self, root, source):
        path = root / "example.core_desc"
        path.write_text(source)
        self.run_module("seal5.frontends.coredsl", path, "-o", root, "--log", "warning")
        self.run_module("seal5.transform.converter", root / "example.m2isarmodel", "--log", "warning")
        return root / "example.seal5model"

    def test_imported_attributes_filter_and_metadata(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            source = FIXTURE.read_text().replace(
                "InstructionSet ArrayNormalization",
                "InstructionSet ArrayNormalization [[drop]] [[arch=xbase]]",
            )
            (root / "base.core_desc").write_text(source)
            model_path = self.parse(
                root,
                'import "base.core_desc"\n'
                "InstructionSet Custom extends ArrayNormalization [[keep]] [[ver=1.20]] "
                "[[experimental]] [[arch=xcvmac]] [[feature=XCVMac]] {\n"
                "instructions {\n"
                "CV_MAC [[keep]] [[skip_pattern_gen]] {\n"
                "encoding: 7'b0000001 :: rs2[4:0] :: rs1[4:0] :: 3'b000 :: rd[4:0] :: 7'b0101011;\n"
                'assembly: {"cv.mac", "{name(rd)}, {name(rs1)}, {name(rs2)}"};\n'
                "behavior: { X[rd] = X[rs1] + X[rs2]; }\n"
                "}\n"
                "CV_OTHER { encoding: 7'b0000010 :: rs2[4:0] :: rs1[4:0] :: 3'b000 :: rd[4:0] :: 7'b0101011; "
                'assembly: {"cv.other", "{name(rd)}, {name(rs1)}, {name(rs2)}"}; '
                "behavior: { X[rd] = X[rs1] + X[rs2]; } }\n"
                "}\n}\n",
            )
            original = load_model(model_path)
            self.assertIn(Seal5InstSetAttribute.DROP, original.sets["ArrayNormalization"].attributes)
            self.run_module(
                "seal5.transform.filter_model.filter",
                model_path,
                "--drop-sets",
                "Custom",
                "--drop-instructions",
                "CV_MAC",
            )
            filtered = load_model(model_path)
            self.assertEqual(set(filtered.sets), {"Custom"})
            instr = list(filtered.sets["Custom"].instructions.values())
            self.assertEqual([item.name for item in instr], ["CV_MAC"])
            self.assertIn(Seal5InstrAttribute.SKIP_PATTERN_GEN, instr[0].attributes)

            settings_path = root / "settings.yaml"
            settings_path.write_text("models:\n  example:\n    extensions:\n      Custom:\n        arch: xoverride\n")
            self.run_module("seal5.transform.process_settings.transform", model_path, "--yaml", settings_path)
            settings = load_model(model_path).sets["Custom"].settings
            self.assertEqual(
                (settings.feature, settings.arch, settings.version, settings.experimental),
                ("XCVMac", "xoverride", "1.20", True),
            )
            self.run_module("seal5.transform.process_settings.transform", model_path, "--yaml", settings_path)
            settings = load_model(model_path).sets["Custom"].settings
            self.assertEqual((settings.arch, settings.version), ("xoverride", "1.20"))
            for module in (
                "collect_register_operands.collect",
                "collect_immediate_operands.collect",
                "collect_operand_types.collect",
                "detect_inouts.collect",
            ):
                self.run_module("seal5.transform." + module, model_path)
            generated = root / "generated.yaml"
            self.run_module("seal5.backends.yaml.writer", model_path, "-o", generated)
            extension = yaml.safe_load(generated.read_text())["models"]["example"]["extensions"]["Custom"]
            self.assertEqual(
                {key: extension[key] for key in ("feature", "arch", "version", "experimental")},
                {"feature": "XCVMac", "arch": "xoverride", "version": "1.20", "experimental": True},
            )

    def test_unannotated_filters_unchanged_and_drop_attribute(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            model_path = self.parse(root, FIXTURE.read_text().replace("STORE_BE {", "STORE_BE [[drop]] {"))
            self.run_module("seal5.transform.filter_model.filter", model_path)
            names = {item.name for item in load_model(model_path).sets["ArrayNormalization"].instructions.values()}
            self.assertEqual(names, {"LOAD_BE", "LOAD24_LE"})

    def test_conflicting_flags_rejected(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            model_path = self.parse(root, FIXTURE.read_text().replace("LOAD_BE {", "LOAD_BE [[keep]] [[drop]] {"))
            message = self.run_module("seal5.transform.filter_model.filter", model_path, success=False)
            self.assertIn("cannot have both keep and drop", message)

    def test_invalid_set_metadata_rejected(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            model_path = self.parse(
                root, FIXTURE.read_text().replace("ArrayNormalization {", "ArrayNormalization [[experimental=maybe]] {")
            )
            yaml = root / "settings.yaml"
            yaml.write_text("models: {}\n")
            message = self.run_module(
                "seal5.transform.process_settings.transform", model_path, "--yaml", yaml, success=False
            )
            self.assertIn("experimental must be", message)

    def test_compat_filter_uses_source_attributes(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            source = (
                FIXTURE.read_text()
                .replace("ArrayNormalization {", "ArrayNormalization [[keep]] {")
                .replace("LOAD_BE {", "LOAD_BE [[keep]] {")
            )
            path = root / "example.core_desc"
            path.write_text(source)
            self.run_module("seal5.frontends.coredsl", path, "-o", root)
            model_path = root / "example.m2isarmodel"
            self.run_module(
                "seal5.transform.filter_model.filter",
                model_path,
                "--compat",
                "--drop-sets",
                "ArrayNormalization",
                "--drop-instructions",
                "LOAD_BE",
            )
            sets = load_model(model_path, compat=True).sets
            self.assertEqual(list(sets), ["ArrayNormalization"])
            self.assertEqual([item.name for item in sets["ArrayNormalization"].instructions.values()], ["LOAD_BE"])

    def test_combined_set_header_attributes_parse(self):
        from m2isar.frontends.coredsl2.utils import make_parser
        from seal5.frontends.coredsl import make_set_attribute_parser

        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "group.core_desc"
            path.write_text("InstructionSet Group combines First, Second [[keep]] [[ver=1.20]];")
            attributes = {}
            parser = make_set_attribute_parser(path, make_parser, attributes)
            tree = parser.description_content()
            name = tree.definitions[0].name
            self.assertEqual(attributes[id(name)], {"keep": None, "ver": "1.20"})


if __name__ == "__main__":
    unittest.main()

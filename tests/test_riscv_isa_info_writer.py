# SPDX-License-Identifier: Apache-2.0
"""Tests for RISCVISAInfo patch generation."""

import unittest
import tempfile
from types import SimpleNamespace
from pathlib import Path
from unittest.mock import patch

import yaml

from seal5.backends.riscv_isa_info import writer
from seal5.backends.riscv_isa_info.writer import gen_riscv_isa_info_metadata, gen_riscv_isa_info_str
from seal5.settings import ExtensionsSettings, LLVMVersion


class RISCVISAInfoWriterTests(unittest.TestCase):
    """Exercise extension implication and incompatibility generation."""

    def test_extension_entry_is_sorted_by_arch_name(self):
        arch, content = gen_riscv_isa_info_str(
            "First", ExtensionsSettings(arch="xfirst"), LLVMVersion(major=18)
        )

        self.assertEqual(arch, "xfirst")
        self.assertIn('{"xfirst", {1, 0}}', content)

    def test_generates_implications_and_deduplicated_incompatibilities(self):
        model_sets = {
            "First": SimpleNamespace(
                settings=ExtensionsSettings(arch="xfirst", implies=["Second"], incompatible=["Third"])
            ),
            "Second": SimpleNamespace(settings=ExtensionsSettings(arch="xsecond")),
            "Third": SimpleNamespace(
                settings=ExtensionsSettings(arch="xthird", incompatible=["First"])
            ),
        }

        implications, incompatible = gen_riscv_isa_info_metadata(model_sets, LLVMVersion(major=17))

        self.assertIn('if (ExtName == "xfirst"', implications)
        self.assertIn('findDefaultVersion("xsecond")', implications)
        self.assertIn('addExtension("xsecond", Version->Major, Version->Minor);', implications)
        self.assertEqual(incompatible.count("extensions are incompatible"), 1)
        self.assertIn("'xfirst' and 'xthird' extensions are incompatible", incompatible)

    def test_uses_llvm_18_add_extension_api(self):
        model_sets = {
            "First": SimpleNamespace(settings=ExtensionsSettings(arch="xfirst", implies=["Second"])),
            "Second": SimpleNamespace(settings=ExtensionsSettings(arch="xsecond")),
        }

        implications, _ = gen_riscv_isa_info_metadata(model_sets, LLVMVersion(major=18))

        self.assertIn('addExtension("xsecond", Version.value());', implications)

    def test_uses_modern_llvm_api_for_versions_19_to_23(self):
        model_sets = {
            "First": SimpleNamespace(
                settings=ExtensionsSettings(arch="xfirst", implies=["Second"], incompatible=["Third"])
            ),
            "Second": SimpleNamespace(settings=ExtensionsSettings(arch="xsecond")),
            "Third": SimpleNamespace(settings=ExtensionsSettings(arch="xthird")),
        }

        for major in range(19, 24):
            with self.subTest(llvm_major=major):
                implications, incompatible = gen_riscv_isa_info_metadata(model_sets, LLVMVersion(major=major))

                self.assertIn('Exts["xsecond"] = *Version;', implications)
                self.assertIn('WorkList.push_back("xsecond");', implications)
                self.assertNotIn("WorkList.count", implications)
                self.assertIn('return getError("\'xfirst\' and \'xthird\' extensions are incompatible");', incompatible)

    def test_modern_llvm_main_emits_only_relation_patches(self):
        model_sets = {
            "First": SimpleNamespace(
                settings=ExtensionsSettings(arch="xfirst", implies=["Second"], incompatible=["Third"])
            ),
            "Second": SimpleNamespace(settings=ExtensionsSettings(arch="xsecond")),
            "Third": SimpleNamespace(settings=ExtensionsSettings(arch="xthird")),
        }
        model = SimpleNamespace(
            settings=SimpleNamespace(llvm=SimpleNamespace(state=SimpleNamespace(version=LLVMVersion(major=19)))),
            sets=model_sets,
        )

        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory) / "riscv_isa_info.patch"
            index = Path(directory) / "index.yml"
            with patch("sys.argv", ["writer", "model.seal5model", "--output", str(output), "--index", str(index)]):
                with patch.object(writer, "load_model", return_value=model):
                    writer.main()

            artifacts = yaml.safe_load(index.read_text())["artifacts"]
            self.assertEqual(
                {artifact["key"] for artifact in artifacts},
                {"riscv_isa_info_implies", "riscv_isa_info_incompatible"},
            )
            self.assertTrue(
                all(artifact["dest_path"] == "llvm/lib/TargetParser/RISCVISAInfo.cpp" for artifact in artifacts)
            )
            self.assertFalse(output.exists())

    def test_parses_implication_and_incompatibility_settings(self):
        settings = ExtensionsSettings.from_dict({"implies": ["Second"], "incompatible": ["Third"]})

        self.assertEqual(settings.implies, ["Second"])
        self.assertEqual(settings.incompatible, ["Third"])

    def test_rejects_unknown_related_extensions(self):
        model_sets = {
            "First": SimpleNamespace(settings=ExtensionsSettings(arch="xfirst", implies=["Missing"])),
        }

        with self.assertRaisesRegex(ValueError, "Unknown extension"):
            gen_riscv_isa_info_metadata(model_sets, LLVMVersion(major=18))

    def test_rejects_invalid_extension_names(self):
        model_sets = {
            "First": SimpleNamespace(
                settings=ExtensionsSettings(arch='xfirst"; injected_code(); //', implies=["Second"])
            ),
            "Second": SimpleNamespace(settings=ExtensionsSettings(arch="xsecond")),
        }

        with self.assertRaisesRegex(ValueError, "Invalid RISCVISAInfo extension name"):
            gen_riscv_isa_info_metadata(model_sets, LLVMVersion(major=18))


if __name__ == "__main__":
    unittest.main()

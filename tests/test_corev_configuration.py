# SPDX-License-Identifier: Apache-2.0
"""The full CoreV demo must not silently drop extensions or orphan intrinsics."""

from pathlib import Path
import re
import unittest
from tempfile import TemporaryDirectory
from types import SimpleNamespace

from seal5.settings import PatchSettings

import yaml


ROOT = Path(__file__).resolve().parents[1] / "examples" / "corev"


class CoreVConfigurationTests(unittest.TestCase):
    def test_intrinsics_reference_real_instructions(self):
        for config in sorted((ROOT / "cfg").glob("XCoreV*.yml")):
            source = ROOT / "cdsl" / f"{config.stem}.core_desc"
            instructions = set(re.findall(r"^\s*(CV_\w+)\s*(?:\[\[.*?\]\]\s*)*\{", source.read_text(), re.MULTILINE))
            data = yaml.safe_load(config.read_text())
            for intrinsic in data.get("intrinsics", {}).get("intrinsics", []):
                with self.subTest(config=config.name, intrinsic=intrinsic["instr_name"]):
                    self.assertEqual(intrinsic["set_name"], config.stem)
                    self.assertIn(intrinsic["instr_name"].removeprefix("SEAL5_"), instructions)
                    name = intrinsic["instr_name"].removeprefix("SEAL5_")
                    block = re.search(
                        r"^\s*" + name + r"\s*(?:\[\[.*?\]\]\s*)*\{(.*?)(?=^\s*CV_\w+\s*(?:\[\[.*?\]\]\s*)*\{|\Z)",
                        source.read_text(),
                        re.MULTILINE | re.DOTALL,
                    ).group(1)
                    encoding = re.search(r"encoding:\s*(.*?);", block, re.DOTALL).group(1)
                    fields = set(re.findall(r"(\w+)\[", encoding))
                    arguments = [argument["arg_name"] for argument in intrinsic["args"]]
                    self.assertEqual(len(arguments), len(set(arguments)))
                    self.assertEqual(intrinsic["ret_type"], "i32")
                    for argument in intrinsic["args"]:
                        self.assertIn(argument["arg_name"], fields)
                        if argument["arg_name"] not in {"rd", "rs1", "rs2", "rs3"}:
                            self.assertTrue(argument.get("immediate"), argument)

    def test_filters_keep_all_corev_instructions(self):
        data = yaml.safe_load((ROOT / "cfg/filter.yml").read_text())["filter"]
        self.assertEqual(data["instructions"]["drop"], [])
        self.assertIn("RV32I", data["sets"]["drop"])
        self.assertIn("RV64I", data["sets"]["drop"])

    def test_capability_patch_skips_updated_dependencies(self):
        data = yaml.safe_load((ROOT / "cfg/llvm22.yml").read_text())
        patch = PatchSettings(**next(p for p in data["patches"] if p["name"] == "corev_packed_capabilities"))
        with TemporaryDirectory() as directory:
            deps = Path(directory)
            features = deps / "cdsl2llvm/llvm/lib/Target/RISCV/RISCVFeatures.td"
            features.parent.mkdir(parents=True)
            settings = SimpleNamespace(deps_dir=deps)
            features.write_text("def FeatureGPR32V;\n")
            self.assertTrue(patch.check_enabled(settings))
            features.write_text("def FeatureGPR32V;\ndef FeatureGPR32VAdd;\n")
            self.assertFalse(patch.check_enabled(settings))

    def test_llvm22_enables_branch_and_memory_patterns(self):
        data = yaml.safe_load((ROOT / "cfg/llvm22.yml").read_text())
        check = data["passes"]["overrides"]["check_pattern_support"]
        self.assertTrue(check["allow_memory"])
        self.assertTrue(check["allow_branches"])
        for name in ("behav_to_llvmir", "behav_to_pat"):
            self.assertFalse(data["passes"]["overrides"][name]["no_extend"])


if __name__ == "__main__":
    unittest.main()

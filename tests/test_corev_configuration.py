# SPDX-License-Identifier: Apache-2.0
"""The full CoreV demo must not silently drop extensions or orphan intrinsics."""

from pathlib import Path
import re
import runpy
import unittest
from tempfile import TemporaryDirectory
from types import SimpleNamespace
from unittest.mock import patch

from seal5.settings import PatchSettings, Seal5Settings

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
        data = yaml.safe_load((ROOT / "cfg/corev.yml").read_text())
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

    def test_feature_capacity_patch_preserves_larger_target_bitsets(self):
        data = yaml.safe_load((ROOT / "cfg/llvm23.yml").read_text())
        entry = next(p for p in data["patches"] if p["name"] == "corev_subtarget_feature_capacity")
        capacity_patch = PatchSettings(**entry)
        with TemporaryDirectory() as directory:
            root = Path(directory)
            settings = Seal5Settings(directory=str(root / "source"), meta_dir=str(root / "metadata"))
            header = settings.source_dir / "llvm/include/llvm/TargetParser/SubtargetFeature.h"
            dependency_header = settings.deps_dir / "cdsl2llvm/llvm/include/llvm/TargetParser/SubtargetFeature.h"
            header.parent.mkdir(parents=True)
            dependency_header.parent.mkdir(parents=True)
            for words, dependency_words in ((6, 7), (7, 6), (8, 6)):
                header.write_text(f"const unsigned MAX_SUBTARGET_WORDS = {words};\n")
                dependency_header.write_text(f"const unsigned MAX_SUBTARGET_WORDS = {dependency_words};\n")
                self.assertEqual(capacity_patch.check_enabled(settings), words == 6)

    def test_shared_config_preserves_branch_memory_and_arithmetic(self):
        data = yaml.safe_load((ROOT / "cfg/corev.yml").read_text())
        check = data["passes"]["overrides"]["check_pattern_support"]
        self.assertTrue(check["allow_memory"])
        self.assertTrue(check["allow_branches"])
        for name in ("behav_to_llvmir", "behav_to_pat"):
            self.assertFalse(data["passes"]["overrides"][name]["no_extend"])

    def test_supported_versions_load_shared_settings_and_same_tests(self):
        from seal5 import wrapper

        inventories = []
        for major, release in ((22, "22.1.8"), (23, "23.1.3")):
            with self.subTest(major=major):
                with patch.object(wrapper, "LLVM_REF", f"llvmorg-{release}"), patch.object(
                    wrapper, "run_seal5_flow"
                ) as run:
                    runpy.run_path(str(ROOT.parent / "corev_demo.py"))
                files = run.call_args.args[0]
                self.assertIn(ROOT / "cfg/corev.yml", files)
                overlay = ROOT / "cfg" / f"llvm{major}.yml"
                self.assertIn(overlay, files)
                data = yaml.safe_load(overlay.read_text())
                self.assertEqual(data["tools"]["pattern_gen"]["ref"], f"llvm-{release}-packed-simd")
                for entry in data["patches"]:
                    self.assertTrue((overlay.parent / entry["file"]).is_file(), entry)
                tests = {p for p in files if p.suffix in (".c", ".s", ".ll")}
                self.assertIn(ROOT / "tests/simd/*.c", tests)
                inventories.append(tests)
        self.assertEqual(*inventories)


if __name__ == "__main__":
    unittest.main()

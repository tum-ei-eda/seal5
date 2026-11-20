# SPDX-License-Identifier: Apache-2.0
"""Example configuration and LLVM patch wiring for RV32 register pairs."""
import unittest


class RegisterPairExampleTests(unittest.TestCase):
    def test_demo_enables_pattern_generation(self):
        from pathlib import Path
        import runpy
        from unittest.mock import patch
        from seal5 import wrapper

        root = Path(__file__).resolve().parents[1]
        with patch.object(wrapper, "LLVM_REF", "llvmorg-23.1.3"), patch.object(wrapper, "run_seal5_flow") as run:
            runpy.run_path(str(root / "examples/regpairs_demo.py"), run_name="__main__")
            self.assertFalse(run.call_args.kwargs["skip_patterns"])
            self.assertFalse(any(p.name == "minimal.yml" for p in run.call_args.args[0]))

    def test_patch_conditions_and_resources_work_on_the_target_source(self):
        from pathlib import Path
        from tempfile import TemporaryDirectory
        import yaml
        from seal5.settings import PatchSettings, Seal5Settings

        config = Path(__file__).resolve().parents[1] / "examples/regpairs/cfg/regpairs.yml"
        data = yaml.safe_load(config.read_text())
        for entry in data["patches"]:
            self.assertTrue((config.parent / entry["file"]).is_file())
        entry = next(p for p in data["patches"] if p["name"] == "regpairs_feature_capacity")
        with TemporaryDirectory() as directory:
            settings = Seal5Settings(directory=directory, meta_dir=directory + "/metadata")
            header = settings.source_dir / "llvm/include/llvm/TargetParser/SubtargetFeature.h"
            header.parent.mkdir(parents=True)
            for words in (6, 7, 8):
                header.write_text(f"const unsigned MAX_SUBTARGET_WORDS = {words};\n")
                self.assertEqual(PatchSettings(**entry).check_enabled(settings), words == 6)

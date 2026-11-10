# SPDX-License-Identifier: Apache-2.0
"""Tests for the Seal5 report stage."""

from pathlib import Path
from types import SimpleNamespace
import tempfile
import unittest
from unittest.mock import Mock, patch

from seal5.flow import Seal5Flow


class ReportStageTests(unittest.TestCase):
    def make_flow(self, root):
        root = Path(root)
        metadata = root / ".seal5"
        models = metadata / "models"
        models.mkdir(parents=True)
        (models / "example.seal5model").touch()

        flow = Seal5Flow.__new__(Seal5Flow)
        flow.meta_dir = metadata
        flow.settings = SimpleNamespace(
            models_dir=models,
            settings_file=metadata / "settings.yml",
        )
        flow.logger = Mock()
        return flow

    def test_generates_workflow_reports_in_default_directory(self):
        with tempfile.TemporaryDirectory() as temporary:
            flow = self.make_flow(temporary)
            with patch("seal5.flow.utils.python") as python:
                flow.report()

            expected = {
                "properties.csv",
                "properties.md",
                "status.csv",
                "status_compact.csv",
                "status.md",
                "status_compact.md",
                "pattern_gen.csv",
                "pattern_gen_agg.csv",
                "pattern_gen.md",
                "pattern_gen_agg.md",
                "test_results.csv",
                "test_results_compact.csv",
                "test_results.md",
                "test_results_compact.md",
                "test_coverage.csv",
                "test_coverage_compact.csv",
                "test_coverage.md",
                "test_coverage_compact.md",
                "diff.csv",
                "diff.md",
                "stage_times.csv",
                "stage_times.md",
                "stage_times.mermaid",
            }
            self.assertEqual(
                {Path(call.args[call.args.index("--output") + 1]).name for call in python.call_args_list},
                expected - {name for name in expected if name.startswith("test_coverage")},
            )
            coverage_paths = {
                Path(call.args[call.args.index("--coverage") + 1]).name
                for call in python.call_args_list
                if "--coverage" in call.args
            }
            self.assertEqual(coverage_paths, {name for name in expected if name.startswith("test_coverage")})
            self.assertEqual(python.call_count, 19)
            self.assertTrue((flow.meta_dir / "reports").is_dir())
            self.assertIn("seal5.backends.report.pattern_gen.writer", python.call_args_list[6].args)

    def test_uses_custom_destination_and_requires_models(self):
        with tempfile.TemporaryDirectory() as temporary:
            flow = self.make_flow(temporary)
            custom_dest = Path(temporary) / "custom-reports"
            with patch("seal5.flow.utils.python"):
                flow.report(dest=custom_dest)
            self.assertTrue(custom_dest.is_dir())

            for model in flow.settings.models_dir.glob("*.seal5model"):
                model.unlink()
            with self.assertRaisesRegex(RuntimeError, "No Seal5 models found"):
                flow.report()


if __name__ == "__main__":
    unittest.main()

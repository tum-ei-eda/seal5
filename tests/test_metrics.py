# SPDX-License-Identifier: Apache-2.0
"""Pass metrics must preserve unavailable measurements through CSV ingestion."""

from pathlib import Path
from tempfile import TemporaryDirectory
import unittest

import pandas as pd
import yaml

from seal5.metrics import read_metrics
from seal5.tools.pattern_metrics import aggregate, instruction_metrics, write_statistics


class MetricsTests(unittest.TestCase):
    def test_pattern_generation_metrics_round_trip(self):
        with TemporaryDirectory() as directory:
            root = Path(directory)
            dest = root / "ADD.td"
            dest.write_text("generated TableGen")
            write_statistics(dest, "Pattern for ADD: pattern", 0.125, returncode=0)
            values = aggregate([instruction_metrics(dest, "tablegen", "success")])
            values["success_instructions"] = ["ADD"]
            values["failed_instructions"] = []
            metrics = root / "metrics.csv"
            # Same serialization used by the PatternGen backend writer.
            pd.DataFrame({key: [value] for key, value in values.items()}).to_csv(metrics, index=False)
            restored = read_metrics(metrics)
            self.assertEqual(restored, values)
            self.assertIsNone(restored["n_tablegen_patterns_imported"])
            self.assertIsNone(restored["n_tablegen_patterns_matched"])
            self.assertEqual(restored["n_tablegen_patterns_imported_known"], 0)
            self.assertEqual(restored["n_tablegen_patterns"], 1)
            self.assertEqual(restored["pattern_gen_time_s"], 0.125)
            # Pass metrics subsequently enter the settings YAML used by reports.
            self.assertEqual(yaml.safe_load(yaml.safe_dump(restored)), values)

    def test_empty_cells_and_existing_literals(self):
        with TemporaryDirectory() as directory:
            metrics = Path(directory) / "metrics.csv"
            metrics.write_text("missing,spaces,zero,explicit_none,empty_string,flag\n,  ,0,None,'',True\n")
            self.assertEqual(
                read_metrics(metrics),
                {
                    "missing": None,
                    "spaces": None,
                    "zero": 0,
                    "explicit_none": None,
                    "empty_string": "",
                    "flag": True,
                },
            )

    def test_malformed_literal_is_still_rejected(self):
        with TemporaryDirectory() as directory:
            metrics = Path(directory) / "metrics.csv"
            metrics.write_text("invalid\nnot_a_literal\n")
            with self.assertRaises(ValueError):
                read_metrics(metrics)


if __name__ == "__main__":
    unittest.main()

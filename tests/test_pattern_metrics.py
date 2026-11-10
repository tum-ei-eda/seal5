# SPDX-License-Identifier: Apache-2.0
"""Pattern counts, unknown validation, failure measurements and aggregation."""

import json
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest
from unittest.mock import patch

import yaml

from seal5.backends.report.pattern_gen.writer import collect_measurements, report_rows, apply_validation
from seal5.tools import cdsl2llvm
from seal5.tools.pattern_metrics import write_statistics, instruction_metrics, parse_statistics, count_gisel_entries

OUTPUT = """Pattern for ADD [add]: (add GPR:$rs1, GPR:$rs2)
=== Statistics Collected ===
  1 pattern-gen - Parsed instruction sets
  1 pattern-gen - Parsed instructions
  2 pattern-gen - Generated patterns
  3 gisel-emitter - Number of patterns imported from SelectionDAG
"""


class PatternMetricsTests(unittest.TestCase):
    def test_multiple_patterns_per_instruction_at_every_report_scope(self):
        with TemporaryDirectory() as directory:
            rows = []
            for name in ("MULSN", "MULHHSN", "MULUN", "MULHHUN"):
                dest = Path(directory) / f"{name}.td"
                dest.write_text("generated")
                output = "".join(f"Pattern for {name}_{n} [mul]: (mul GPR:$a, GPR:$b)\n" for n in range(32))
                output += "=== Statistics Collected ===\n32 pattern-gen - Generated patterns\n"
                write_statistics(dest, output, 0.25, returncode=0)
                rows.append(
                    {
                        "model": "COREV",
                        "set": "MAC",
                        "instruction": name,
                        "mode": "tablegen",
                        "status": "success",
                        **instruction_metrics(dest, "tablegen", "success"),
                    }
                )
            for row in report_rows(rows):
                count = 32 if row["scope"] == "instruction" else 128
                self.assertEqual(row["n_extracted_patterns"], count)
                self.assertEqual(row["n_tablegen_patterns"], count)
                self.assertEqual(row["n_instructions"], 1 if count == 32 else 4)
                self.assertIsNone(row["n_tablegen_patterns_imported"])
                self.assertIsNone(row["n_tablegen_patterns_matched"])

    def test_direct_entry_permutations(self):
        table = (
            "for (int R_0 = 0; R_0 < 2; R_0++)\n"
            "for (int R_1 = 0; R_1 < 3; R_1++)\n"
            "{\nRuleMatcher RM{Locs};\n}\n"
            "{\nRuleMatcher RM{Locs};\n}\n"
        )
        self.assertEqual(count_gisel_entries(table), 7)
        self.assertIsNone(count_gisel_entries("unknown emitter syntax"))

    def test_empty_report(self):
        result = report_rows([], "global")[0]
        self.assertEqual(result["n_instructions"], 0)
        self.assertEqual(result["n_gisel_table_entries"], 0)

    def test_all_statistics_groups(self):
        stats = parse_statistics(OUTPUT)
        self.assertEqual(stats["gisel-emitter"]["Number of patterns imported from SelectionDAG"], 3)

    def test_modes_sizes_and_unknown_validation(self):
        with TemporaryDirectory() as root:
            dest = Path(root) / "ADD.td"
            dest.write_bytes(b"tablegen\n")
            dest.with_suffix(".inc").write_bytes(b"direct matcher\n")
            for direct in (False, True):
                write_statistics(dest, OUTPUT, 0.125, gisel_table=direct, returncode=0)
                mode = "gisel_table" if direct else "tablegen"
                row = instruction_metrics(dest, mode, "success")
                self.assertEqual(row[f"n_{mode}_patterns"], 2)
                self.assertEqual(row["n_extracted_patterns"], 2)
                self.assertIsNone(row[f"n_{mode}_patterns_matched"])
                self.assertEqual(row["tablegen_bytes"], 9)
                self.assertEqual(row["gisel_table_bytes"], 15 if direct else 0)
                self.assertEqual(row[f"{mode}_time_s"], 0.125)
                if not direct:
                    # Unrelated whole-backend importer counters are not attributed to this instruction.
                    self.assertIsNone(row["n_tablegen_patterns_imported"])

    def test_failure_records_time_and_ignores_stale_outputs(self):
        with TemporaryDirectory() as root:
            root = Path(root)
            (root / "bin").mkdir()
            (root / "bin" / "pattern-gen").touch()
            dest = root / "ADD.td"
            dest.write_text("old output")
            Path(str(dest) + ".stats").write_text("old statistics")

            def fail(*args, **kwargs):
                kwargs["handle_exit"](1, OUTPUT)
                raise AssertionError("tool failed")

            with patch.object(cdsl2llvm.utils, "exec_getout", side_effect=fail):
                with self.assertRaises(AssertionError):
                    cdsl2llvm.run_pattern_gen(root, root / "ADD.core_desc", dest)
            measured = yaml.safe_load(Path(str(dest) + ".stats").read_text())["seal5"]
            self.assertEqual(measured["returncode"], 1)
            self.assertEqual(measured["tablegen_bytes"], 0)
            self.assertGreaterEqual(measured["generation_time_s"], 0)
            self.assertEqual(measured["n_patterns"], 2)

    def test_aggregation_distinct_sets_and_incomplete_evidence(self):
        with TemporaryDirectory() as root:
            root = Path(root)
            rows = []
            for model, name, instr, mode, status in (
                ("M1", "S", "A", "tablegen", "success"),
                ("M1", "S", "B", "gisel_table", "success"),
                ("M2", "S", "A", "tablegen", "success"),
                ("M2", "T", "C", "tablegen", "skipped"),
            ):
                dest = root / model / name / f"{instr}.td"
                dest.parent.mkdir(parents=True, exist_ok=True)
                dest.write_text("generated")
                write_statistics(dest, OUTPUT, 0.25, gisel_table=mode == "gisel_table")
                rows.append(
                    {
                        "model": model,
                        "set": name,
                        "instruction": instr,
                        "mode": mode,
                        "status": status,
                        **instruction_metrics(dest, mode, status),
                    }
                )
            evidence = [
                {
                    "model": "M1",
                    "set": "S",
                    "instruction": "A",
                    "mode": "tablegen",
                    "imported": [0, 1],
                    "imported_source": "import.json",
                    "matched": [1],
                    "matched_source": "coverage.json",
                }
            ]
            apply_validation(rows, evidence)
            result = report_rows(rows)
            total = result[-1]
            self.assertEqual(total["n_sets"], 3)
            self.assertEqual(total["n_processed_sets"], 2)
            self.assertEqual(total["n_processed_instructions"], 3)
            self.assertEqual(total["n_extracted_patterns"], 6)
            self.assertEqual(total["n_tablegen_patterns"], 4)
            self.assertEqual(total["n_gisel_table_patterns"], 2)
            self.assertEqual(total["tablegen_time_s"], 0.5)
            self.assertEqual(total["gisel_table_time_s"], 0.25)
            self.assertIsNone(total["n_tablegen_patterns_imported"])
            self.assertEqual(total["n_tablegen_patterns_imported_known"], 2)
            self.assertEqual(total["n_tablegen_patterns_imported_unreported_instructions"], 1)
            # A current-run manifest excludes stale sidecars from previous runs.
            (root / "M1" / "pattern_gen_manifest.json").write_text(
                json.dumps({"schema_version": 1, "instructions": rows[:1]})
            )
            found = collect_measurements(root)
            self.assertEqual(len(found), 3)

    def test_direct_pattern_and_expanded_entry_evidence(self):
        with TemporaryDirectory() as root:
            dest = Path(root) / "A.td"
            dest.with_suffix(".inc").write_text("for (int R_0 = 0; R_0 < 4; R_0++)\n{\nRuleMatcher RM{Locs};\n}\n")
            write_statistics(dest, "Pattern for A: pattern", 1, gisel_table=True)
            row = {
                "model": "M",
                "set": "S",
                "instruction": "A",
                "mode": "gisel_table",
                "status": "success",
                **instruction_metrics(dest, "gisel_table", "success"),
            }
            evidence = {
                "model": "M",
                "set": "S",
                "instruction": "A",
                "mode": "gisel_table",
                "matched": [0],
                "matched_source": "root-coverage.json",
                "matched_entries": [1, 3],
                "matched_entries_source": "entry-coverage.json",
            }
            apply_validation([row], [evidence])
            self.assertEqual(row["n_gisel_table_patterns_matched"], 1)
            self.assertEqual(row["n_gisel_table_entries_matched"], 2)
            with self.assertRaises(ValueError):
                apply_validation([row], [{**evidence, "imported": [0], "imported_source": "invalid"}])

    def test_formats_only(self):
        with TemporaryDirectory() as root:
            dest = Path(root) / "A.td"
            dest.write_bytes(b"instruction")
            dest.with_name("AInstrFormat.td").write_bytes(b"format")
            write_statistics(dest, OUTPUT, 1, skip_patterns=True)
            row = instruction_metrics(dest, "formats", "success")
            self.assertEqual(row["n_extracted_patterns"], 0)
            self.assertEqual(row["tablegen_bytes"], 17)
            self.assertEqual(row["pattern_gen_time_s"], 1)
            self.assertEqual(row["tablegen_time_s"], 0)
            self.assertEqual(row["gisel_table_time_s"], 0)

    def test_llvmir_is_not_tablegen_size(self):
        with TemporaryDirectory() as root:
            dest = Path(root) / "A.ll"
            dest.write_bytes(b"LLVM IR")
            stats = write_statistics(dest, "", 1, skip_patterns=True, skip_formats=True)
            self.assertEqual(stats["seal5"]["mode"], "llvmir")
            self.assertEqual(stats["seal5"]["tablegen_bytes"], 0)

    def test_invalid_evidence(self):
        with TemporaryDirectory() as root:
            dest = Path(root) / "A.td"
            write_statistics(dest, OUTPUT, 1)
            row = {
                "model": "M",
                "set": "S",
                "instruction": "A",
                "mode": "tablegen",
                "status": "success",
                **instruction_metrics(dest, "tablegen", "success"),
            }
            for indices in ([2], [0, 0], [-1], [True]):
                with self.subTest(indices=indices), self.assertRaises(ValueError):
                    apply_validation(
                        [row],
                        [
                            {
                                "model": "M",
                                "set": "S",
                                "instruction": "A",
                                "mode": "tablegen",
                                "matched": indices,
                                "matched_source": "test",
                            }
                        ],
                    )


if __name__ == "__main__":
    unittest.main()

# SPDX-License-Identifier: Apache-2.0
"""Skipped operand-type failures must remain actionable and preserve progress."""
import logging
from types import SimpleNamespace
import unittest
from unittest.mock import patch

from seal5.transform.collect_operand_types import collect


class OperandTypeDiagnosticsTests(unittest.TestCase):
    def test_skip_reports_cause_and_traceback_then_visits_next_instruction(self):
        broken = SimpleNamespace(name="BROKEN", operands={}, operation=object())
        good = SimpleNamespace(name="GOOD", operands={}, operation=object())
        model = SimpleNamespace(sets={"test": SimpleNamespace(name="test", instructions={0: broken, 1: good})})
        args = collect.get_parser().parse_args(["input.seal5model", "--skip-failing", "-o", "output.seal5model"])
        logger = logging.getLogger("test.operand_type_diagnostics")
        with patch.object(collect, "load_model", return_value=model), patch.object(
            collect, "dump_model"
        ) as dump, patch.object(collect, "CollectOperandTypesVisitor") as visitor, patch.object(
            collect, "logger", logger
        ):
            visitor.return_value.generate.side_effect = [ValueError("conflicting immediate signedness"), None]
            with self.assertLogs(logger, level="WARNING") as captured:
                collect.run(args)
            self.assertEqual(visitor.return_value.generate.call_count, 2)
            dump.assert_called_once_with(model, "output.seal5model", compat=False)
        self.assertIn("BROKEN: ValueError: conflicting immediate signedness", captured.output[0])
        self.assertIn("Traceback (most recent call last)", captured.output[0])
        self.assertIsNotNone(captured.records[0].exc_info)

    def test_without_skip_propagates_failure_without_writing_output(self):
        instr = SimpleNamespace(name="BROKEN", operands={}, operation=object())
        model = SimpleNamespace(sets={"test": SimpleNamespace(name="test", instructions={0: instr})})
        args = collect.get_parser().parse_args(["input.seal5model"])
        failure = ValueError("invalid cast")
        with patch.object(collect, "load_model", return_value=model), patch.object(
            collect, "dump_model"
        ) as dump, patch.object(collect, "CollectOperandTypesVisitor") as visitor:
            visitor.return_value.generate.side_effect = failure
            with self.assertRaises(ValueError) as raised:
                collect.run(args)
            self.assertIs(raised.exception, failure)
            dump.assert_not_called()

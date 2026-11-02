# SPDX-License-Identifier: Apache-2.0
"""Experimental patterns must remain opt-in and exclude multiple results."""

from types import SimpleNamespace
import unittest
from unittest.mock import patch

from m2isar.metamodel import attribute_info, behav

from seal5.model import Seal5InstrAttribute as Instr, Seal5OperandAttribute as Operand
from seal5.transform.check_pattern_support import check


class ExperimentalPatternSupportTests(unittest.TestCase):
    def check_instructions(self, *flags):
        def instruction(name, outputs, *attributes):
            operands = {"rs1": SimpleNamespace(attributes={Operand.IN: []})}
            for index in range(outputs):
                operands[f"rd{index}"] = SimpleNamespace(attributes={Operand.OUT: []})
            return SimpleNamespace(
                name=name,
                size=32,
                operands=operands,
                attributes={attribute: [] for attribute in attributes},
                operation=behav.Operation([behav.Literal(1)]),
            )

        instructions = {
            item.name: item
            for item in (
                instruction("load", 1, Instr.MAY_LOAD),
                instruction("store", 0, Instr.MAY_STORE),
                instruction("branch", 0, Instr.IS_BRANCH, attribute_info.InstrAttribute.COND),
                instruction("raw_branch", 0, attribute_info.InstrAttribute.COND),
                instruction("multi", 2),
                instruction("load_multi", 2, Instr.MAY_LOAD),
                instruction("store_and_register", 1, Instr.MAY_STORE),
                instruction("read_modify_write", 1, Instr.MAY_LOAD, Instr.MAY_STORE),
                instruction("arithmetic", 1),
            )
        }
        model = SimpleNamespace(sets={"Test": SimpleNamespace(name="Test", instructions=instructions)})
        args = check.get_parser().parse_args(["test.seal5model", *flags])
        with patch.object(check, "load_model", return_value=model), patch.object(check, "dump_model"):
            check.run(args)
        return {name for name, instr in instructions.items() if Instr.SKIP_PATTERN_GEN not in instr.attributes}

    def test_default(self):
        self.assertEqual(self.check_instructions(), {"arithmetic"})

    def test_memory_opt_in(self):
        self.assertEqual(self.check_instructions("--allow-memory"), {"arithmetic", "load", "store"})

    def test_branch_opt_in(self):
        self.assertEqual(self.check_instructions("--allow-branches"), {"arithmetic", "branch"})

    def test_both(self):
        self.assertEqual(
            self.check_instructions("--allow-memory", "--allow-branches"),
            {"arithmetic", "load", "store", "branch"},
        )


if __name__ == "__main__":
    unittest.main()

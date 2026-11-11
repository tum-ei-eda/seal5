# SPDX-License-Identifier: Apache-2.0
"""Post-increment punctuation must not become an operand or close parentheses."""

import unittest

from seal5.model import Seal5Instruction


class PostincrementAssemblyTests(unittest.TestCase):
    def instruction(self):
        instruction = object.__new__(Seal5Instruction)
        instruction.operands = {name: None for name in ("rd", "imm", "rs1")}
        return instruction

    def test_memory_syntax(self):
        for syntax in (
            "{name(rd)}, {imm}({name(rs1)})",
            "{name(rd)}, {imm}({name(rs1)}!)",
            "{name(rd)}, {imm}({name(rs1)})!",
        ):
            with self.subTest(syntax=syntax):
                self.instruction().check_asm_str(syntax)

    def test_missing_closing_parenthesis(self):
        with self.assertRaisesRegex(AssertionError, "Missing"):
            self.instruction().check_asm_str("{name(rd)}, {imm}({name(rs1)}!")

    def test_duplicate_operand_is_rejected(self):
        with self.assertRaisesRegex(AssertionError, "Duplicate"):
            self.instruction().check_asm_str("{name(rd)}, {imm}({name(rs1)}!), {name(rd)}")


if __name__ == "__main__":
    unittest.main()

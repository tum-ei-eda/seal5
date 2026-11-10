# SPDX-License-Identifier: Apache-2.0
"""Destination guard normalization is explicitly scoped to configured operands."""

from types import SimpleNamespace
import unittest

from m2isar.metamodel import behav
from seal5.transform.eliminate_rd_cmp_zero.visitor import EliminateRdCmpZeroVisitor


class DestinationGuardTests(unittest.TestCase):
    def guard(self, name, operator="!=", value=0):
        return behav.BinaryOperation(
            behav.NamedReference(SimpleNamespace(name=name)), behav.Operator(operator), behav.Literal(value)
        )

    def test_default_preserves_other_operand_guards(self):
        visitor = EliminateRdCmpZeroVisitor()
        self.assertEqual(visitor.generate(self.guard("rd"), None).value, 1)
        for name in ("rd1", "rd2", "rs1"):
            self.assertIsInstance(visitor.generate(self.guard(name), None), behav.BinaryOperation)

    def test_explicit_destinations(self):
        visitor = EliminateRdCmpZeroVisitor(("rd1", "rd2"))
        for name in ("rd1", "rd2"):
            self.assertEqual(visitor.generate(self.guard(name), None).value, 1)
        for expression in (self.guard("rs1"), self.guard("rd1", "=="), self.guard("rd2", value=1)):
            self.assertIsInstance(visitor.generate(expression, None), behav.BinaryOperation)


if __name__ == "__main__":
    unittest.main()

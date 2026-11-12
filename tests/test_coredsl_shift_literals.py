# SPDX-License-Identifier: Apache-2.0
"""Shift data width must survive CoreDSL serialization after constant folding."""

from types import SimpleNamespace
import unittest

from m2isar.metamodel import behav
from m2isar.metamodel.type_info import PrimitiveType, TypeKind

from seal5.backends.coredsl2.utils import Seal5CoreDSL2Writer
from seal5.backends.coredsl2.visitor import Seal5CDSLWriterVisitor


def render(expr):
    visitor = Seal5CDSLWriterVisitor()
    writer = Seal5CoreDSL2Writer(visitor)
    visitor.generate(expr, writer)
    return writer.text


class ShiftLiteralTests(unittest.TestCase):
    def test_word_constant_with_narrow_shift_count(self):
        count = behav.NamedReference(SimpleNamespace(name="count", ty=PrimitiveType(TypeKind.UINT, 5)))
        for width in (32, 64):
            literal = behav.Literal(1, PrimitiveType(TypeKind.UINT, width))
            for left in (literal, behav.Group(literal)):
                expr = behav.BinaryOperation(left, behav.Operator("<<"), count)
                self.assertEqual(render(expr), f"((unsigned<{width}>)1) << (count)")

    def test_signed_constant_right_shift(self):
        literal = behav.Literal(-1, PrimitiveType(TypeKind.INT, 32))
        expr = behav.BinaryOperation(literal, behav.Operator(">>"), behav.Literal(3))
        self.assertEqual(render(expr), "((signed<32>)-1) >> (3)")

    def test_other_operations_keep_their_serialization(self):
        literal = behav.Literal(1, PrimitiveType(TypeKind.UINT, 32))
        expr = behav.BinaryOperation(literal, behav.Operator("+"), behav.Literal(2))
        self.assertEqual(render(expr), "(1) + (2)")


if __name__ == "__main__":
    unittest.main()

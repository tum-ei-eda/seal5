# SPDX-License-Identifier: Apache-2.0
"""Widening immediate expressions must not change their encoding types."""
import unittest

from m2isar.metamodel import arch, behav
from m2isar.metamodel.type_info import TypeKind
from seal5.model import DataType, Seal5ImmOperand, Seal5Type
from seal5.transform.collect_operand_types.collect import VisitorContext
from seal5.transform.collect_operand_types.visitor import CollectOperandTypesVisitor


class OperandTypeWideningTests(unittest.TestCase):
    def context(self, signed=False):
        kind = TypeKind.INT if signed else TypeKind.UINT
        field = arch.BitFieldDescr("imm", 6, kind)
        operand = Seal5ImmOperand("imm", Seal5Type(DataType.S if signed else DataType.U, 6, 1), {}, [])
        return field, operand, VisitorContext({"imm": operand})

    def test_widening_keeps_encoded_width_and_source_signedness(self):
        for signed in (False, True):
            for target_kind in (TypeKind.INT, TypeKind.UINT):
                for width in (8, 16, 32, 64):
                    with self.subTest(signed=signed, target=target_kind, width=width):
                        field, operand, context = self.context(signed)
                        expr = behav.TypeConv(target_kind, width, behav.NamedReference(field))
                        result = CollectOperandTypesVisitor().generate(expr, context)
                        self.assertIs(result, expr)
                        self.assertEqual(expr.size, width)
                        self.assertEqual(operand.ty.width, 6)
                        self.assertEqual(operand.ty.datatype, DataType.S if signed else DataType.U)

    def test_same_width_cast_still_collects_signed_immediate(self):
        field, operand, context = self.context()
        expr = behav.TypeConv(TypeKind.INT, 6, behav.NamedReference(field))
        CollectOperandTypesVisitor().generate(expr, context)
        self.assertEqual(operand.ty.datatype, DataType.S)
        self.assertEqual(operand.ty.width, 6)

    def test_truncation_still_fails_without_changing_operand_type(self):
        field, operand, context = self.context()
        expr = behav.TypeConv(TypeKind.INT, 3, behav.NamedReference(field))
        with self.assertRaisesRegex(AssertionError, "truncation"):
            CollectOperandTypesVisitor().generate(expr, context)
        self.assertEqual(operand.ty.datatype, DataType.U)
        self.assertEqual(operand.ty.width, 6)

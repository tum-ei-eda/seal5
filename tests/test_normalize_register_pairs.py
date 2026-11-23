# SPDX-License-Identifier: Apache-2.0
"""XP is an emission view; rewriting it must preserve word order and aliasing."""
import unittest

from m2isar.metamodel import arch, behav
from m2isar.metamodel.type_info import PrimitiveType, TypeKind
from seal5.transform.normalize_register_pairs import NormalizeRegisterPairs


class NormalizeRegisterPairsTests(unittest.TestCase):
    def setUp(self):
        self.bank = arch.RegisterBank("X", 32, TypeKind.UINT, 32, {})
        self.index = arch.BitFieldDescr("rs1", 5, TypeKind.UINT)
        self.other = arch.BitFieldDescr("rs2", 5, TypeKind.UINT)
        self.visitor = NormalizeRegisterPairs(["rs1", "rs2"])

    def word(self, offset=0, index=None):
        base = behav.NamedReference(index or self.index)
        if offset:
            base = behav.BinaryOperation(base, behav.Operator("+"), behav.Literal(offset))
        return behav.IndexedReference(self.bank, base)

    def test_concatenation_becomes_one_64_bit_view(self):
        original = behav.ConcatOperation(behav.Group(self.word(1)), behav.Group(self.word()))
        result = self.visitor.generate(original)
        self.assertIsInstance(result, behav.IndexedReference)
        self.assertEqual(result.reference.name, "XP")
        self.assertEqual(result.ty.size, 64)
        self.assertIs(result.index.reference, self.index)
        self.assertEqual(result.reference.ty.length, 32)
        self.assertEqual(self.bank.name, "X")
        self.assertEqual(self.bank.ty.element_type.size, 32)

    def test_mismatched_or_reversed_words_are_not_collapsed(self):
        for high, low in ((self.word(1, self.other), self.word()), (self.word(), self.word(1))):
            result = self.visitor.generate(behav.ConcatOperation(high, low))
            self.assertIsInstance(result, behav.ConcatOperation)
            self.assertIsInstance(result.left, behav.SliceOperation)
            self.assertIsInstance(result.right, behav.SliceOperation)

    def test_unmarked_registers_remain_ordinary_words(self):
        visitor = NormalizeRegisterPairs([])
        result = visitor.generate(behav.ConcatOperation(self.word(1), self.word()))
        self.assertEqual(result.left.reference.name, "X")
        self.assertEqual(result.right.reference.name, "X")

    def test_individual_words_use_explicit_slices(self):
        for offset in (0, 1):
            result = self.visitor.generate(self.word(offset))
            self.assertEqual(result.expr.reference.name, "XP")
            self.assertEqual((result.left.value, result.right.value), (offset * 32 + 31, offset * 32))
        with self.assertRaises(ValueError):
            self.visitor.generate(self.word(2))

    def stores(self, source, second_source=None):
        return [
            behav.Assignment(self.word(), behav.SliceOperation(source, behav.Literal(31), behav.Literal(0))),
            behav.Assignment(
                self.word(1), behav.SliceOperation(second_source or source, behav.Literal(63), behav.Literal(32))
            ),
        ]

    def test_complete_local_result_is_stored_once(self):
        variable = arch.Variable("result", PrimitiveType(TypeKind.UINT, 64), attributes={})
        result = self.visitor.generate(self.stores(behav.NamedReference(variable)))
        self.assertEqual(len(result), 1)
        self.assertIsInstance(result[0].target, behav.IndexedReference)
        self.assertEqual(result[0].target.reference.name, "XP")
        self.assertIs(result[0].expr.reference, variable)

    def test_alias_sensitive_or_different_values_are_not_merged(self):
        result = self.visitor.generate(self.stores(self.word(), self.word(1)))
        self.assertEqual(len(result), 2)
        a = arch.Variable("a", PrimitiveType(TypeKind.UINT, 64), attributes={})
        b = arch.Variable("b", PrimitiveType(TypeKind.UINT, 64), attributes={})
        result = self.visitor.generate(self.stores(behav.NamedReference(a), behav.NamedReference(b)))
        self.assertEqual(len(result), 2)

    def test_nonadjacent_writes_are_not_merged(self):
        variable = arch.Variable("result", PrimitiveType(TypeKind.UINT, 64), attributes={})
        low, high = self.stores(behav.NamedReference(variable))
        result = self.visitor.generate([low, behav.Break(), high])
        self.assertEqual(len(result), 3)

    def test_inference_finds_only_complete_reads_and_safe_stores(self):
        from seal5.transform.infer_register_pairs import InferRegisterPairs

        variable = arch.Variable("result", PrimitiveType(TypeKind.UINT, 64), attributes={})
        cases = [
            (behav.ConcatOperation(self.word(1), self.word()), {"rs1"}),
            (self.stores(behav.NamedReference(variable)), {"rs1"}),
            (behav.ConcatOperation(self.word(), self.word(1)), set()),
            (behav.ConcatOperation(self.word(1, self.other), self.word()), set()),
            (behav.ConcatOperation(self.word(8), self.word()), set()),
            (self.stores(self.word(), self.word(1)), set()),
            (self.word(1), set()),
        ]
        for operation, expected in cases:
            with self.subTest(expected=expected, operation=operation):
                inference = InferRegisterPairs(["rs1", "rs2"])
                inference.generate(operation)
                self.assertEqual(inference.pairs, expected)

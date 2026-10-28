# SPDX-License-Identifier: Apache-2.0
"""Verify access normalization before integrating with pattern generation."""

import unittest
from types import SimpleNamespace

from m2isar.metamodel import behav
from m2isar.metamodel.type_info import ArrayType, PrimitiveType, TypeKind

from seal5.transform.explicit_names import ExplicitNames
from seal5 import pass_list


def symbol(name, width):
    return SimpleNamespace(name=name, ty=ArrayType(PrimitiveType(TypeKind.UINT, width), 32))


def plus(base, offset):
    return behav.BinaryOperation(base, behav.Operator("+"), behav.Literal(offset))


class ExplicitNamesTests(unittest.TestCase):
    def test_memory_widths_and_xlen(self):
        for xlen in (32, 64):
            for count in (1, 2, 4, 8):
                with self.subTest(xlen=xlen, count=count):
                    memory = symbol("MEM", 8)
                    address = behav.NamedReference(symbol("addr", xlen))
                    access = behav.IndexedReference(memory, plus(address, count - 1), address)
                    visitor = ExplicitNames(xlen, memory=True)
                    result = visitor.generate(access)
                    width = count * 8
                    self.assertEqual(result.reference.name, "MEMX" if width == xlen else f"MEM{width}")
                    self.assertIs(result.index, address)
                    self.assertIsNone(result.right)
                    self.assertEqual(result.ty.size, width)
                    self.assertEqual(memory.name, "MEM")
                    self.assertEqual(memory.ty.element_type.size, 8)
                    self.assertIs(visitor.generate(result), result)
                    self.assertEqual(visitor.changed, 1)

    def test_byte_and_unsupported_accesses(self):
        memory = symbol("MEM", 8)
        address = behav.NamedReference(symbol("addr", 32))
        visitor = ExplicitNames(32, memory=True)
        self.assertEqual(visitor.generate(behav.IndexedReference(memory, address)).reference.name, "MEM8")
        for left, right in ((plus(address, 2), address), (address, plus(address, 1))):
            access = behav.IndexedReference(memory, left, right)
            self.assertIs(visitor.generate(access), access)
        # Same spelling does not imply identical local variables.
        other = behav.NamedReference(symbol("addr", 32))
        access = behav.IndexedReference(memory, plus(address, 1), other)
        self.assertIs(visitor.generate(access), access)

    def test_nested_load_store_and_register_word(self):
        registers = symbol("X", 64)
        memory = symbol("MEM", 8)
        index = behav.Literal(1)
        word = behav.SliceOperation(
            behav.Group(behav.IndexedReference(registers, index)), behav.Literal(31), behav.Literal(0)
        )
        store = behav.Assignment(behav.IndexedReference(memory, behav.Literal(0)), word)
        tree = behav.Operation([behav.Conditional([behav.Literal(1)], [[store]])])
        visitor = ExplicitNames(64, memory=True, registers=True)
        visitor.generate(tree)
        self.assertEqual(store.target.reference.name, "MEM8")
        self.assertEqual(store.expr.reference.name, "XW")
        self.assertEqual(store.expr.ty.size, 32)
        self.assertEqual(registers.name, "X")
        self.assertEqual(registers.ty.element_type.size, 64)
        self.assertEqual(visitor.changed, 2)

    def test_disabled_and_rv32(self):
        word = behav.SliceOperation(
            behav.IndexedReference(symbol("X", 32), behav.Literal(1)), behav.Literal(31), behav.Literal(0)
        )
        self.assertIs(ExplicitNames(32, registers=True).generate(word), word)
        access = behav.IndexedReference(symbol("MEM", 8), behav.Literal(0))
        self.assertIs(ExplicitNames(32).generate(access), access)
        # Disabled pipeline passes must not even open a model file.
        self.assertFalse(pass_list.explicit_memory_names("missing").metrics["enabled"])
        self.assertFalse(pass_list.explicit_register_names("missing").metrics["enabled"])


if __name__ == "__main__":
    unittest.main()

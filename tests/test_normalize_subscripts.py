# SPDX-License-Identifier: Apache-2.0
"""Check scalar range width/direction and serialization."""

import pickle
import unittest

from m2isar.metamodel import behav

from test_explicit_names import plus, symbol
from seal5.backends.coredsl2.utils import Seal5CoreDSL2Writer
from seal5.backends.coredsl2.visitor import Seal5CDSLWriterVisitor
from seal5.transform.normalize_subscripts import IndexedPartSelect, NormalizeSubscripts


def render(expr):
    visitor = Seal5CDSLWriterVisitor()
    writer = Seal5CoreDSL2Writer(visitor)
    writer.visitor.generate(expr, writer)
    return writer.text


class SubscriptTests(unittest.TestCase):
    def test_dynamic_scalar_both_directions(self):
        for ascending in (False, True):
            base = behav.NamedReference(symbol("base", 32))
            upper = plus(base, 4)
            left, right = (base, upper) if ascending else (upper, base)
            source = behav.NamedReference(symbol("temp", 32))
            original = behav.SliceOperation(source, left, right)
            visitor = NormalizeSubscripts(32)
            result = visitor.generate(original)
            self.assertIsInstance(result, IndexedPartSelect)
            self.assertEqual(result.width, 5)
            self.assertEqual(render(result), "temp[base +: 5]")
            self.assertEqual(render(pickle.loads(pickle.dumps(result))), "temp[base +: 5]")
            self.assertIs(visitor.generate(result), result)
            self.assertEqual(visitor.changed, 1)

    def test_value_semantics(self):
        # Exhaustively compare all 8-bit values and valid 3-bit selections.
        base_expr = behav.NamedReference(symbol("base", 32))
        source = behav.NamedReference(symbol("temp", 8))
        original = behav.SliceOperation(source, plus(base_expr, 2), base_expr)
        normalized = NormalizeSubscripts(32).generate(original)
        self.assertIs(normalized.base.reference, base_expr.reference)
        for value in range(256):
            for base in range(6):
                expected = (value >> base) & ((1 << normalized.width) - 1)
                for left, right in ((base + 2, base), (base, base + 2)):
                    result = sum(
                        ((value >> bit) & 1) << (bit - min(left, right))
                        for bit in range(min(left, right), max(left, right) + 1)
                    )
                    self.assertEqual(result, expected)

    def test_array_range_is_expanded_in_order(self):
        base = behav.NamedReference(symbol("addr", 32))
        access = behav.IndexedReference(symbol("MEM", 8), base, plus(base, 3))
        result = NormalizeSubscripts(32).generate(access)
        output = render(result)
        self.assertIn("MEM[addr]", output)
        self.assertIn("MEM[(addr) + (3)]", output)
        self.assertEqual(output.count(" :: "), 3)
        self.assertNotIn("addr:", output)

    def test_unknown_width_is_preserved(self):
        original = behav.SliceOperation(
            behav.NamedReference(symbol("temp", 32)),
            behav.NamedReference(symbol("left", 32)),
            behav.NamedReference(symbol("right", 32)),
        )
        self.assertIs(NormalizeSubscripts(32).generate(original), original)


if __name__ == "__main__":
    unittest.main()

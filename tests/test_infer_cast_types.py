# SPDX-License-Identifier: Apache-2.0
"""Signed branch-immediate casts must survive inference and serialization."""

import unittest

from m2isar.metamodel import arch, behav
from m2isar.metamodel.type_info import TypeKind

from seal5.transform.infer_types.visitor import InferTypesMutator, WarningsManager
from test_normalize_subscripts import render


class CastTypeTests(unittest.TestCase):
    def test_signedness_and_width_round_trip(self):
        for source_kind, cast_kind in ((TypeKind.UINT, TypeKind.INT), (TypeKind.INT, TypeKind.UINT)):
            for width in (3, 5, 8, 32, 64):
                for explicit_width in (None, width, 64):
                    with self.subTest(source=source_kind, cast=cast_kind, width=width, explicit=explicit_width):
                        operand = arch.Register("constant", source_kind, width, {})
                        expr = behav.TypeConv(cast_kind, explicit_width, behav.NamedReference(operand))
                        visitor = InferTypesMutator()
                        for _ in range(2):
                            visitor.generate(expr, WarningsManager(None))
                            self.assertEqual(expr.ty.kind, cast_kind)
                            self.assertEqual(expr.ty.size, explicit_width or width)
                            sign = "signed" if cast_kind == TypeKind.INT else "unsigned"
                            self.assertEqual(render(expr), f"({sign}<{explicit_width or width}>)(constant)")
                            self.assertEqual(operand.ty.kind, source_kind)


if __name__ == "__main__":
    unittest.main()

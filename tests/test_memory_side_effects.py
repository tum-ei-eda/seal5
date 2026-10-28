# SPDX-License-Identifier: Apache-2.0
"""Memory normalization needs correct load/store flags before pattern filtering."""

import unittest

from m2isar.metamodel import arch, behav, attribute_info, type_info

from seal5.transform.detect_side_effects.collect import VisitorContext
from seal5.transform.detect_side_effects.visitor import DetectSideEffectsVisitor


class MemorySideEffectTests(unittest.TestCase):
    def test_load_and_store_flags(self):
        for name, width in (("MEM", 8), ("MEM16", 16), ("MEMX", 64)):
            memory = arch.Memory(
                name, type_info.TypeKind.UINT, width, 1024, {attribute_info.MemoryAttribute.IS_MAIN_MEM: []}
            )
            for write in (False, True):
                with self.subTest(name=name, write=write):
                    access = behav.IndexedReference(memory, behav.Literal(8))
                    target, value = (access, behav.Literal(1)) if write else (behav.Literal(0), access)
                    context = VisitorContext()
                    DetectSideEffectsVisitor().generate(behav.Assignment(target, value), context)
                    self.assertEqual(context.may_store, write)
                    self.assertEqual(context.may_load, not write)


if __name__ == "__main__":
    unittest.main()

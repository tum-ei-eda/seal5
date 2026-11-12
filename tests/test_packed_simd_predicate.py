# SPDX-License-Identifier: Apache-2.0
"""Packed representation and actual ISA predicates must both survive export."""
import unittest

from seal5.backends.patterngen.writer import require_packed_simd_feature


class PackedSIMDPredicateTests(unittest.TestCase):
    def test_preserve_isa_and_xlen_predicates(self):
        source = "let Predicates = [HasMySIMD,IsRV32] in {\ndef I : Inst<(outs GPR32V4:$rd)>;\n}\n"
        result = require_packed_simd_feature(source)
        self.assertIn("[HasMySIMD, IsRV32, HasGPR32V]", result)
        self.assertEqual(require_packed_simd_feature(result), result)

    def test_existing_feature_not_duplicated(self):
        result = require_packed_simd_feature("let Predicates = [HasGPR32V,IsRV32] in { GPR32V2 }")
        self.assertEqual(result.count("HasGPR32V"), 1)

    def test_scalar_patterns_unchanged(self):
        source = "def : Pat<(add GPR:$a, GPR:$b), (I GPR:$a, GPR:$b)>;"
        self.assertEqual(require_packed_simd_feature(source), source)

    def test_no_existing_predicates(self):
        result = require_packed_simd_feature("def I : Inst<(outs GPR32V2:$rd)>;")
        self.assertTrue(result.startswith("let Predicates = [HasGPR32V] in {"))


if __name__ == "__main__":
    unittest.main()

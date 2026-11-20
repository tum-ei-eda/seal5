# SPDX-License-Identifier: Apache-2.0
"""Pair legalization and ISA predicates must both survive export."""
import unittest

from seal5.backends.patterngen.writer import require_register_pair_feature


class RegisterPairPredicateTests(unittest.TestCase):
    def test_preserve_isa_and_xlen_predicates(self):
        source = "let Predicates = [HasMySIMD,IsRV32] in {\ndef I : Inst<(outs GPRPairRV32:$rd)>;\n}\n"
        result = require_register_pair_feature(source)
        self.assertIn("[HasMySIMD, IsRV32, HasSeal5RegPair32]", result)
        self.assertEqual(require_register_pair_feature(result), result)

    def test_existing_feature_not_duplicated(self):
        result = require_register_pair_feature("let Predicates = [HasSeal5RegPair32,IsRV32] in { GPRPair }")
        self.assertEqual(result.count("HasSeal5RegPair32"), 1)

    def test_scalar_patterns_unchanged(self):
        source = "def : Pat<(add GPR:$a, GPR:$b), (I GPR:$a, GPR:$b)>;"
        self.assertEqual(require_register_pair_feature(source), source)

    def test_no_existing_predicates(self):
        result = require_register_pair_feature("def I : Inst<(outs GPRPair:$rd)>;")
        self.assertTrue(result.startswith("let Predicates = [HasSeal5RegPair32] in {"))

    def test_arithmetic_capabilities_are_independent(self):
        for op in ("add", "sub", "mul"):
            source = f"let Predicates = [HasMySIMD,IsRV32] in {{ (v2i32 ({op} GPRPair:$a, GPRPair:$b)) }}"
            result = require_register_pair_feature(source)
            self.assertIn("HasSeal5RegPair32" + op.title(), result)
            for other in {"add", "sub", "mul"} - {op}:
                self.assertNotIn("HasSeal5RegPair32" + other.title(), result)
            self.assertEqual(require_register_pair_feature(result), result)

    def test_scalar_subtraction_node_gets_subtraction_capability(self):
        result = require_register_pair_feature("(riscv_seal5_sub64 GPRPair:$a, GPRPair:$b)")
        self.assertIn("HasSeal5RegPair32Sub", result)
        self.assertNotIn("HasSeal5RegPair32Add", result)


if __name__ == "__main__":
    unittest.main()

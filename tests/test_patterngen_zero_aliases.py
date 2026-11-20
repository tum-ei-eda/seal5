# SPDX-License-Identifier: Apache-2.0
"""Equivalent zero specializations must not require mutually exclusive encodings."""

from pathlib import Path
from tempfile import TemporaryDirectory
from types import SimpleNamespace
import unittest

from seal5.backends.patterngen.writer import allow_equivalent_zero_specializations


class ZeroAliasTests(unittest.TestCase):
    def write(self, root, name, pattern, predicate="HasExample", flags="mayLoad = 0, mayStore = 0"):
        dest = root / f"{name}.td"
        dest.write_text(
            f'let Predicates = [{predicate}] in {{\nlet hasSideEffects = 0, {flags}, '
            'isBranch = 0, isTerminator = 0, Constraints = "" in '
            f"def {name}_ : RVInst_{name}<(outs GPR:$rd), (ins GPR:$a)>;\n}}\n"
        )
        Path(str(dest) + ".out").write_text(f"Pattern for {name}_0 [test.{name}]: {pattern}\n")
        test = dest.with_suffix(".test-cg.ll")
        test.write_text(
            "\n".join(
                f"define void @impl{name}_{n}() {{\n"
                f"  ; RV32-MIR: {{{{^ *[^;]*}}}} {name}_{{{{[ ,]}}}}\n"
                f"  ; RV32-ASM: test.{name}\n  ret void\n}}"
                for n in (0, 1)
            )
        )
        return SimpleNamespace(name=name), test

    def test_equivalent_zero_trees_allow_both_encodings_only_at_zero(self):
        with TemporaryDirectory() as directory:
            root = Path(directory)
            a, a_test = self.write(root, "A", "(add GPR:$a, GPR:$b)")
            b, b_test = self.write(root, "B", "(add GPR:$a, GPR:$b)")
            allow_equivalent_zero_specializations(root, [a, b])
            for test in (a_test, b_test):
                zero, nonzero = test.read_text().split("define void @impl" + test.stem.split(".")[0] + "_1")
                self.assertIn("{{(A_|B_)}}", zero)
                self.assertIn(r"{{(test\.A|test\.B)([ \t]|$)}}", zero)
                self.assertNotIn("A_|B_", nonzero)
            before = a_test.read_text()
            allow_equivalent_zero_specializations(root, [a, b])
            self.assertEqual(a_test.read_text(), before)

    def test_different_semantics_predicates_and_memory_keep_exact_checks(self):
        for options in (
            {"pattern": "(sub GPR:$a, GPR:$b)"},
            {"pattern": "(add GPR:$a, GPR:$b)", "predicate": "HasOther"},
            {"pattern": "(add GPR:$a, GPR:$b)", "flags": "mayLoad = 1, mayStore = 0"},
        ):
            with self.subTest(options=options), TemporaryDirectory() as directory:
                root = Path(directory)
                a, test = self.write(root, "A", "(add GPR:$a, GPR:$b)")
                b, _ = self.write(root, "B", **options)
                before = test.read_text()
                allow_equivalent_zero_specializations(root, [a, b])
                self.assertEqual(test.read_text(), before)


if __name__ == "__main__":
    unittest.main()

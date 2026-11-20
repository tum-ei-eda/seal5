# SPDX-License-Identifier: Apache-2.0
"""Verify current metamodel behaviors are exported to DOT."""

import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace

from m2isar.metamodel import behav

from seal5.backends.dot.viewer import build_tree, export_tree


class DotBackendTests(unittest.TestCase):
    def test_exports_model_and_behavior(self):
        function = SimpleNamespace(
            extern=False,
            ty="i32",
            throws=(),
            attributes={},
            args={},
            operation=behav.Operation([behav.Literal(42)]),
        )
        set_def = SimpleNamespace(
            constants={"ANSWER": SimpleNamespace(value=42)},
            memories={},
            memory_aliases={},
            functions={"answer": function},
            instructions={},
        )
        root = build_tree(SimpleNamespace(sets={"Example": set_def}), include_operations=True)

        literal = next(node for node in root.descendants if node.name == "Literal")
        self.assertEqual(literal.value, 42)

        with tempfile.TemporaryDirectory() as output_dir:
            output_path = export_tree(root, Path(output_dir) / "model.dot")
            dot_source = output_path.read_text(encoding="utf-8")

        self.assertIn("Example", dot_source)
        self.assertIn("42", dot_source)


if __name__ == "__main__":
    unittest.main()

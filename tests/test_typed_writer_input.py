"""The compiler frontend accepts artifacts from the shared typed writer."""
from pathlib import Path
import pickle
import subprocess
import sys
import tempfile
import unittest


class TypedWriterInputTests(unittest.TestCase):
    def test_operand_metadata_and_inherited_only_set(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            source = root / "typed.core_desc"
            source.write_text('''InstructionSet Parent {
    architectural_state { register unsigned<32> X[32] [[is_main_reg]]; }
    instructions {
        CUSTOM {
            operands: { unsigned<5> rd [[out]] [[is_reg]]; }
            encoding: 20'b0 :: rd[4:0] :: 7'b0001011;
            behavior: { X[rd] = 42; }
        }
    }
}
InstructionSet Aggregate extends Parent {}
''')
            result = subprocess.run(
                [sys.executable, "-m", "seal5.frontends.coredsl2_seal5.parser",
                 str(source), "--output", str(root / "models")],
                capture_output=True, text=True,
            )
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            models = pickle.loads((root / "models/typed.m2isarmodel").read_bytes())
            self.assertEqual(models["Aggregate"].extension, ["Parent"])
            instruction, = models["Parent"].instructions.values()
            self.assertEqual(instruction.name, "CUSTOM")
            self.assertIn("rd", instruction.fields)


if __name__ == "__main__":
    unittest.main()

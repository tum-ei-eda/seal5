# SPDX-License-Identifier: Apache-2.0
"""Keep machine-readable stdout records intact when diagnostics use stderr."""

import sys
import unittest

from seal5.utils import exec_getout


class SubprocessStreamTests(unittest.TestCase):
    def test_partial_stdout_is_not_interrupted_by_stderr(self):
        program = (
            "import os; os.write(1, b'Pattern for TEST'); "
            "os.write(2, b'=== Statistics Collected ===\\n'); "
            "os.write(1, b' [test]: (add GPR:$a, GPR:$b)\\n')"
        )
        output = exec_getout(sys.executable, "-c", program, live=True, separate_stderr=True, print_func=lambda _: None)
        self.assertEqual(output.splitlines()[0], "Pattern for TEST [test]: (add GPR:$a, GPR:$b)")
        self.assertIn("=== Statistics Collected ===", output)


if __name__ == "__main__":
    unittest.main()

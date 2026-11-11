# SPDX-License-Identifier: Apache-2.0
"""IR and pattern extraction must use the same requested arithmetic rules."""

from pathlib import Path
from tempfile import TemporaryDirectory
from types import SimpleNamespace
import unittest
from unittest.mock import patch

from seal5 import pass_list


class CoreDSLTypingTests(unittest.TestCase):
    def test_typing_mode_reaches_both_writers(self):
        for handler in (pass_list.convert_behav_to_llvmir, pass_list.convert_behav_to_tablegen):
            for no_extend in (False, True):
                with self.subTest(handler=handler.__name__, no_extend=no_extend), TemporaryDirectory() as directory:
                    root = Path(directory)
                    (root / "Example.seal5model").touch()
                    settings = SimpleNamespace(models_dir=root, temp_dir=root)
                    with patch.object(pass_list.utils, "python") as invoke, patch.object(
                        pass_list, "read_metrics", return_value={}
                    ):
                        handler("Example", settings=settings, no_extend=no_extend)
                    self.assertEqual("--coredsl-typing" in invoke.call_args.args, not no_extend)


if __name__ == "__main__":
    unittest.main()

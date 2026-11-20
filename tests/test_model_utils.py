"""Dotted model basenames must survive transform serialization."""
import pickle
from pathlib import Path
import tempfile
import unittest

from seal5.model_utils import dump_model


class ModelFilenameTest(unittest.TestCase):
    def test_model_names(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            for compat in (False, True):
                suffix = ".m2isarmodel" if compat else ".seal5model"
                for name in ("XIsaac", "XIsaac.splitted", "XIsaac.splitted" + suffix):
                    with self.subTest(name=name, compat=compat):
                        target = root / name
                        dump_model({"marker": name}, target, compat=compat)
                        expected = target if name.endswith(suffix) else root / (name + suffix)
                        self.assertEqual(pickle.loads(expected.read_bytes()), {"marker": name})

    def test_wrong_model_suffix(self):
        with tempfile.TemporaryDirectory() as directory:
            for compat, wrong in ((False, ".m2isarmodel"), (True, ".seal5model")):
                with self.subTest(compat=compat), self.assertRaises(AssertionError):
                    dump_model({}, Path(directory) / ("wrong" + wrong), compat=compat)

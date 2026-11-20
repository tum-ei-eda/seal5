# SPDX-License-Identifier: Apache-2.0
"""Bundled patch fallback must retain the path that can actually be applied."""

from pathlib import Path
from tempfile import TemporaryDirectory
import unittest

from seal5.flow import lookup_manual_patch
from seal5.settings import PatchSettings


class PatchLookupTests(unittest.TestCase):
    def test_relative_default_resolves_to_bundled_patch(self):
        patch = PatchSettings(name="gitignore", target="llvm", file="gitignore.patch")
        resolved = lookup_manual_patch(patch)
        self.assertTrue(resolved.is_file())
        self.assertEqual(Path(patch.file), resolved)

    def test_explicit_patch_path_is_preserved(self):
        with TemporaryDirectory() as directory:
            path = Path(directory) / "custom.patch"
            path.touch()
            patch = PatchSettings(name="custom", target="llvm", file=str(path))
            self.assertEqual(lookup_manual_patch(patch), path)
            self.assertEqual(patch.file, str(path))


if __name__ == "__main__":
    unittest.main()

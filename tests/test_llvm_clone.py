# SPDX-License-Identifier: Apache-2.0
"""LLVM initialization must tolerate metadata created by the wrapper's cleanup."""

from pathlib import Path
import tempfile
import unittest

import git

from seal5.flow import Seal5Flow
from seal5.tools.llvm import clone_llvm_repo, open_llvm_repo


class LLVMCloneTests(unittest.TestCase):
    def test_clone_preserves_preexisting_metadata(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            source = root / "source"
            repo = git.Repo.init(source)
            (source / "README").write_text("local LLVM fixture\n")
            repo.index.add(["README"])
            actor = git.Actor("Seal5 Test", "seal5@example.com")
            commit = repo.index.commit("Initial fixture", author=actor, committer=actor)
            repo.create_tag("llvmorg-22.1.8")
            dest = root / "dest"
            metadata = dest / ".seal5"
            (metadata / "temp").mkdir(parents=True)
            marker = metadata / "temp" / "keep.txt"
            marker.write_text("preserve me")
            self.assertIsNone(Seal5Flow(dest).repo)
            cloned, sha, version = clone_llvm_repo(
                dest, source.as_uri(), ref="llvmorg-22.1.8", refresh=True, depth=1, progress=False
            )
            self.assertEqual(sha, commit.hexsha)
            self.assertEqual(version, {"major": 22, "minor": 1, "patch": 8})
            self.assertEqual(marker.read_text(), "preserve me")
            self.assertEqual((dest / "README").read_text(), "local LLVM fixture\n")
            self.assertEqual(open_llvm_repo(dest).head.commit.hexsha, sha)
            # Reusing a clone without refreshing must still return a valid repository.
            reused, reused_sha, _ = clone_llvm_repo(dest, source.as_uri(), progress=False)
            self.assertEqual(reused_sha, sha)
            reused.close()
            cloned.close()
            repo.close()

    def test_non_repository_user_files_are_rejected(self):
        with tempfile.TemporaryDirectory() as temporary:
            dest = Path(temporary)
            marker = dest / "keep.txt"
            marker.write_text("user data")
            with self.assertRaises(git.InvalidGitRepositoryError):
                clone_llvm_repo(dest, "unused", progress=False)
            self.assertEqual(marker.read_text(), "user data")

    def test_custom_metadata_directory(self):
        with tempfile.TemporaryDirectory() as temporary:
            dest = Path(temporary)
            metadata = dest / "custom-state"
            metadata.mkdir()
            self.assertIsNone(open_llvm_repo(dest, metadata))

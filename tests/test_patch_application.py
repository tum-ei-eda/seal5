# SPDX-License-Identifier: Apache-2.0
"""Tests for applying and staging LLVM patches."""

from pathlib import Path
import tempfile
import unittest
from unittest import mock

import git
import yaml

from seal5.flow import Seal5Flow
from seal5.settings import PatchSettings
from seal5.types import PatchStage


class PatchApplicationTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name)
        self.directory = self.root / "llvm"
        self.repo = git.Repo.init(self.directory)
        self.addCleanup(self.repo.close)
        with self.repo.config_writer() as config:
            config.set_value("user", "name", "Seal5 Test")
            config.set_value("user", "email", "seal5@example.com")
        (self.directory / "file.txt").write_text("start\nend\n")
        self.repo.index.add(["file.txt"])
        self.repo.index.commit("Initial fixture")
        (Path(self.repo.git_dir) / "info" / "exclude").write_text(".seal5/\n")
        self.flow = Seal5Flow(self.directory)
        self.flow.meta_dir.mkdir()
        self.patch_file = self.root / "change.patch"
        (self.directory / "file.txt").write_text("start\nchanged\nend\n")
        self.patch_file.write_text(self.repo.git.diff() + "\n")
        self.repo.git.restore("file.txt")

    def test_clean_patch_stages_without_add_and_commits(self):
        patch = PatchSettings(name="change", target="llvm", file=str(self.patch_file), comment="Test change")
        with mock.patch.object(git.Git, "add", create=True, side_effect=AssertionError("unexpected git add")):
            self.flow.apply_patch(patch)
        self.assertEqual((self.directory / "file.txt").read_text(), "start\nchanged\nend\n")
        self.assertEqual(self.repo.head.commit.message, f"{self.flow.settings.git.prefix} Test change")
        self.assertTrue(patch.applied)
        self.assertFalse(self.repo.is_dirty(untracked_files=True))

    def test_allowed_untracked_files_are_staged_as_before(self):
        generated = self.directory / "generated"
        generated.mkdir()
        (generated / "extra.txt").write_text("extra\n")
        patch = PatchSettings(name="change", target="llvm", file=str(self.patch_file))
        self.flow.apply_patch(patch)
        self.assertEqual(self.repo.head.commit.tree["generated/extra.txt"].data_stream.read(), b"extra\n")
        self.assertFalse(self.repo.is_dirty(untracked_files=True))

    def test_new_ignored_file_is_not_committed(self):
        (self.directory / ".gitignore").write_text("ignored*\n")
        self.repo.git.add(".gitignore")
        self.repo.index.commit("Ignore files")
        with self.patch_file.open("a") as patch_file:
            patch_file.write("--- /dev/null\n+++ b/ignored[1]\n@@ -0,0 +1 @@\n+ignored content\n")
            patch_file.write("--- /dev/null\n+++ b/keep.txt\n@@ -0,0 +1 @@\n+kept content\n")
        patch = PatchSettings(name="change", target="llvm", file=str(self.patch_file))
        self.flow.apply_patch(patch)
        self.assertEqual((self.directory / "ignored[1]").read_text(), "ignored content\n")
        self.assertNotIn("ignored[1]", self.repo.head.commit.tree)
        self.assertEqual(self.repo.head.commit.tree["keep.txt"].data_stream.read(), b"kept content\n")
        self.assertFalse(self.repo.is_dirty(untracked_files=True))

    def test_dirty_rejection_and_force(self):
        (self.directory / "file.txt").write_text("dirty\n")
        patch = PatchSettings(name="change", target="llvm", file=str(self.patch_file))
        with self.assertRaisesRegex(RuntimeError, "not clean"):
            self.flow.apply_patch(patch)
        self.assertEqual((self.directory / "file.txt").read_text(), "dirty\n")
        self.assertFalse(patch.applied)
        self.flow.apply_patch(patch, force=True)
        self.assertEqual((self.directory / "file.txt").read_text(), "start\nchanged\nend\n")
        self.assertTrue(patch.applied)

    def test_generated_patches_keep_sequential_markers_and_test_paths(self):
        (self.directory / "file.txt").write_text(
            "file.txt - example - INSERTION_START\nfile.txt - example - INSERTION_END\n"
        )
        self.repo.git.add("file.txt")
        self.repo.index.commit("Add marker")
        patches_dir = self.flow.settings.patches_dir / "llvm"
        patches_dir.mkdir(parents=True)
        for name in ("first", "second"):
            index = self.root / f"{name}.yml"
            index.write_text(
                yaml.safe_dump(
                    {
                        "artifacts": [
                            {"dest_path": "file.txt", "key": "example", "content": name},
                            {"dest_path": f"llvm/test/{name}.txt", "content": name, "is_test": True},
                        ],
                        "extensions": [],
                    }
                )
            )
            patch = PatchSettings(name=name, target="llvm", index=str(index), generated=True)
            self.flow.apply_patch(patch)
            self.assertTrue(patch.applied)
        self.assertEqual(
            (self.directory / "file.txt").read_text(),
            "file.txt - example - INSERTION_START\nfirst\nsecond\nfile.txt - example - INSERTION_END\n",
        )
        self.assertEqual(self.flow.settings.test.paths[-2:], ["first.txt", "second.txt"])
        self.assertFalse(self.repo.is_dirty(untracked_files=True))

    def test_combined_patch_uses_same_fast_path(self):
        self.repo.create_tag(f"seal5-{self.flow.name}-base")
        combined = self.flow.settings.patches_dir / "stages" / "PHASE_0.patch"
        combined.parent.mkdir(parents=True)
        combined.write_text(self.patch_file.read_text())
        patch = PatchSettings(name="change", target="llvm", file=str(self.patch_file), stage=PatchStage.PHASE_0)
        with mock.patch.object(self.flow, "collect_patches", return_value={PatchStage.PHASE_0: [patch]}):
            with mock.patch.object(git.Git, "add", create=True, side_effect=AssertionError("unexpected git add")):
                self.flow.patch(stages=[PatchStage.PHASE_0], use_combined_patches=True)
        self.assertEqual((self.directory / "file.txt").read_text(), "start\nchanged\nend\n")
        self.assertFalse(self.repo.is_dirty(untracked_files=True))

    def test_failed_patch_does_not_stage_changes(self):
        self.patch_file.write_text(self.patch_file.read_text().replace("start", "missing"))
        patch = PatchSettings(name="change", target="llvm", file=str(self.patch_file))
        before = self.repo.head.commit.hexsha
        with self.assertRaises(git.GitCommandError):
            self.flow.apply_patch(patch)
        self.assertEqual(self.repo.head.commit.hexsha, before)
        self.assertFalse(patch.applied)
        self.assertFalse(self.repo.is_dirty(untracked_files=True))

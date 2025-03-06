#
# Copyright (c) 2023 TUM Department of Electrical and Computer Engineering.
#
# This file is part of Seal5.
# See https://github.com/tum-ei-eda/seal5.git for further info.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
"""LLVM utils for seal5."""
import re
import os
import shutil
from pathlib import Path
from typing import List, Optional, Union

import git
from git import RemoteProgress
from tqdm import tqdm

from seal5 import utils
from seal5.logging import get_logger
from seal5.tools.git import get_author_from_settings
from seal5.settings import GitSettings, CcacheSettings

logger = get_logger()


def lookup_ccache():
    candidates = ["sccache", "ccache"]
    for candidate in candidates:
        found = shutil.which(candidate)
        if found:
            return found
    return None  # Not found


def check_llvm_repo(path: Path):
    repo = git.Repo(path)
    if repo.is_dirty(untracked_files=True):
        # Filter out .seal5/ directory
        out = repo.git.status("--porcelain")
        lines = out.split("\n")
        dirty = []
        for line in lines:
            _, file = line.strip().split(" ", 1)
            if file == ".seal5/":
                continue
            dirty.append(file)
        if len(dirty) > 0:
            logger.debug("Dirty files in LLVM repository: %s", ", ".join(dirty))
            return False

    return True


class CloneProgress(RemoteProgress):
    def __init__(self):
        super().__init__()
        self.pbar = tqdm()

    def update(self, op_code, cur_count, max_count=None, message=""):
        self.pbar.total = max_count
        self.pbar.n = cur_count
        self.pbar.refresh()


def clone_llvm_repo(
    dest: Path,
    clone_url: str,
    ref: Optional[str] = None,
    refresh: bool = False,
    label: str = "default",
    git_settings: GitSettings = None,
    depth: Optional[int] = None,
    default_major_version: int = 18,
    progress: bool = True,  # TODO: default to False and expose to flow.py
):
    sha = None
    version_info = {}
    repo = None
    if dest.is_dir() and utils.is_populated(dest):
        if refresh:
            logger.debug("Refreshing LLVM repository: %s", dest)
            repo = git.Repo(dest)
            repo.remotes.origin.set_url(clone_url)
            repo.remotes.origin.fetch()
            if ref:
                repo.git.checkout(ref)
                if ref not in repo.tags:
                    repo.git.pull("origin", ref)
    else:
        logger.debug("Cloning LLVM repository: %s", clone_url)
        if progress:
            clone_progress = CloneProgress()
        else:
            clone_progress = None
        no_checkout = ref is not None
        branch = None
        depth = depth if depth is not None and depth >= 0 else None
        if depth is not None and ref is not None:
            # assert "llvmorg" in ref  # Needs to be a valid branch name, not a tag
            branch = ref
        repo = git.Repo.clone_from(
            clone_url, dest, no_checkout=no_checkout, branch=branch, depth=depth, progress=clone_progress
        )
        if ref:
            logger.debug("Checking out branch: %s", ref)
            repo.git.checkout(ref)
    # Set author in repo config
    author = get_author_from_settings(git_settings)
    with repo.config_writer() as writer:
        writer.set_value("user", "name", author.name)
        writer.set_value("user", "email", author.email)
    # repo.create_tag(f"seal5-{label}-base", "-f", author=author)
    repo.create_tag(f"seal5-{label}-base", "-f")
    # git describe --tags --match "llvmorg-[0-9]*.[0-9]*.[0-9]*"
    try:
        describe = repo.git.describe("--tags", "--match", "llvmorg-[0-9]*.[0-9]*.[0-9]*")
    except git.GitCommandError:
        describe = None
    if describe:
        splitted = describe.split("-", 3)
        base = splitted[0]
        assert base == "llvmorg"
        version = splitted[1]
        major, minor, patch = version.split(".")
        version_info["major"] = int(major)
        version_info["minor"] = int(minor)
        version_info["patch"] = int(patch)
        rest = splitted[2] if len(splitted) > 2 else ""
        if "rc" in rest:
            rc = rest.split("-", 1)[0][2:]
            version_info["rc"] = int(rc)
    else:
        if default_major_version is not None:
            version_info["major"] = default_major_version

    sha = repo.head.commit.hexsha
    return repo, sha, version_info


def build_llvm(
    src: Path,
    dest: Path,
    target: str = "all",
    debug: Optional[bool] = None,
    use_ninja: Optional[bool] = None,
    verbose: bool = False,
    cmake_options: Optional[dict] = None,
    install: bool = False,
    install_dir: Optional[Union[str, Path]] = None,
    ccache_settings: Optional[CcacheSettings] = None,
):
    if cmake_options is None:
        cmake_options = {}
    if install:
        assert install_dir is not None
        assert Path(install_dir).parent.is_dir()
        cmake_options["CMAKE_INSTALL_PREFIX"] = str(install_dir)
    env = os.environ.copy()
    if ccache_settings:
        if ccache_settings.enable:
            ccache_executable = ccache_settings.executable
            ccache_directory = ccache_settings.directory
            if ccache_executable is None:
                ccache_executable = "auto"

            if ccache_executable == "auto":
                ccache_executable = lookup_ccache()
                assert ccache_executable is not None, "Could not resolve ccache executable"
            cmake_options["CMAKE_C_COMPILER_LAUNCHER"] = ccache_executable
            cmake_options["CMAKE_CXX_COMPILER_LAUNCHER"] = ccache_executable
            if ccache_directory is not None:
                env["CCACHE_DIR"] = ccache_directory
    cmake_args = utils.get_cmake_args(cmake_options)
    dest.mkdir(exist_ok=True)
    utils.cmake(
        src / "llvm",
        *cmake_args,
        use_ninja=use_ninja,
        debug=debug,
        cwd=dest,
        env=env,
        print_func=logger.info if verbose else logger.debug,
        live=True,
    )
    if install:
        assert target is None
        target = "install"
    utils.make(
        target=target, cwd=dest, print_func=logger.info if verbose else logger.debug, live=True, use_ninja=use_ninja
    )


def test_llvm(base: Path, build_dir: Path, test_paths: Optional[List[str]] = None, verbose: bool = False):
    if test_paths is None:
        test_paths = []
    env = os.environ.copy()
    old_path = env["PATH"]
    env["PATH"] = f"{build_dir}/bin:{old_path}"
    lit_exe = build_dir / "bin" / "llvm-lit"
    passed_tests = []
    failing_tests = []
    for test_path in test_paths:

        def handler(_code, _out):
            return 0

        out = utils.exec_getout(
            lit_exe,
            base / test_path,
            print_func=logger.info if verbose else logger.debug,
            live=True,
            env=env,
            handle_exit=handler,
        )
        failing = re.compile(r"FAIL: LLVM :: (.*) \(").findall(out)
        if len(failing) > 0:
            failing_tests.extend(failing)
        passed = re.compile(r"PASS: LLVM :: (.*) \(").findall(out)
        if len(passed) > 0:
            passed_tests.extend(passed)

    return passed_tests, failing_tests


def detect_llvm_imm_types(llvm_dir: Union[str, Path]):
    def get_grep_cmd(prefix):
        return f"grep -r \"def {prefix}imm\" llvm/lib/Target/RISCV | cut -d':' -f2 | tr -s ' ' | sed -e \"s/def //g\""

    def _parse_output(output):
        output = output.strip()
        return set(map(lambda x: x.strip(), output.splitlines()))

    uimm_types = _parse_output(
        utils.exec_getout(get_grep_cmd("u"), shell=True, print_func=lambda *_: None, live=False, cwd=llvm_dir)
    )
    simm_types = _parse_output(
        utils.exec_getout(get_grep_cmd("s"), shell=True, print_func=lambda *_: None, live=False, cwd=llvm_dir)
    )

    imm_types = uimm_types | simm_types
    return imm_types

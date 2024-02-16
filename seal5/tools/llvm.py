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
from pathlib import Path
from typing import List, Optional

import git

from seal5.logging import get_logger
from seal5 import utils

logger = get_logger()


def check_llvm_repo(path: Path):
    repo = git.Repo(path)
    if repo.is_dirty(untracked_files=True):
        # Filter out .seal5/ directory
        out = repo.git.status("--porcelain")
        lines = out.split("\n")
        dirty = []
        for line in lines:
            mode, file = line.strip().split(" ", 1)
            if file == ".seal5/":
                continue
            else:
                dirty.append(file)
        if len(dirty) > 0:
            logger.debug("Dirty files in LLVM repository: %s", ", ".join(dirty))
            return False

    return True


def clone_llvm_repo(
    dest: Path, clone_url: str, ref: Optional[str] = None, refresh: bool = False, label: str = "default"
):
    sha = None
    if dest.is_dir():
        if refresh:
            logger.debug("Refreshing LLVM repository: %s", dest)
            repo = git.Repo(dest)
            repo.remotes.origin.set_url(clone_url)
            repo.remotes.origin.fetch()
            if ref:
                repo.git.checkout(ref)
                repo.git.pull("origin", ref)
            repo.create_tag(f"seal5-{label}-base", "-f")
            sha = repo.head.commit.hexsha
    else:
        logger.debug("Cloning LLVM repository: %s", clone_url)
        repo = git.Repo.clone_from(clone_url, dest, no_checkout=ref is not None)
        if ref:
            logger.debug("Checking out branch: %s", ref)
            repo.git.checkout(ref)
        repo.create_tag(f"seal5-{label}-base", "-f")
        sha = repo.head.commit.hexsha
    return sha


def build_llvm(
    src: Path,
    dest: Path,
    debug: Optional[bool] = None,
    use_ninja: Optional[bool] = None,
    verbose: bool = False,
    cmake_options: dict = {},
):
    cmake_args = utils.get_cmake_args(cmake_options)
    dest.mkdir(exist_ok=True)
    utils.cmake(
        src / "llvm",
        *cmake_args,
        use_ninja=use_ninja,
        debug=debug,
        cwd=dest,
        print_func=logger.info if verbose else logger.debug,
        live=True,
    )
    utils.make(cwd=dest, print_func=logger.info if verbose else logger.debug, live=True)


def test_llvm(base: Path, build_dir: Path, test_paths: List[str] = [], verbose: bool = False):
    lit_exe = build_dir / "bin" / "llvm-lit"
    failing_tests = []
    for test_path in test_paths:

        def handler(code, out):
            return 0

        out = utils.exec_getout(
            lit_exe,
            base / test_path,
            print_func=logger.info if verbose else logger.debug,
            live=True,
            handle_exit=handler,
        )
        failing = re.compile(r"FAIL: LLVM :: (.*) \(").findall(out)
        if len(failing) > 0:
            failing_tests.extend(failing)

    return failing_tests

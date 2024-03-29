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
from pathlib import Path
from typing import List, Optional

import git

from seal5 import utils
from seal5.logging import get_logger
from seal5.tools.git import get_author_from_settings
from seal5.settings import GitSettings

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
    dest: Path,
    clone_url: str,
    ref: Optional[str] = None,
    refresh: bool = False,
    label: str = "default",
    git_settings: GitSettings = None,
):
    sha = None
    version_info = {}
    repo = None
    if dest.is_dir():
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
        repo = git.Repo.clone_from(clone_url, dest, no_checkout=ref is not None)
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
    describe = repo.git.describe("--tags", "--match", "llvmorg-[0-9]*.[0-9]*.[0-9]*")
    if describe:
        splitted = describe.split("-", 3)
        base = splitted[0]
        assert base == "llvmorg"
        version = splitted[1]
        major, minor, patch = version.split(".")
        version_info["major"] = int(major)
        version_info["minor"] = int(minor)
        version_info["patch"] = int(patch)
        rest = splitted[2]
        if "rc" in rest:
            rc = rest.split("-", 1)[0][2:]
            version_info["rc"] = int(rc)

    sha = repo.head.commit.hexsha
    return repo, sha, version_info


def build_llvm(
    src: Path,
    dest: Path,
    target: str = "all",
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
    utils.make(
        target=target, cwd=dest, print_func=logger.info if verbose else logger.debug, live=True, use_ninja=use_ninja
    )


def test_llvm(base: Path, build_dir: Path, test_paths: List[str] = [], verbose: bool = False):
    env = os.environ.copy()
    old_path = env["PATH"]
    env["PATH"] = f"{build_dir}/bin:{old_path}"
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
            env=env,
            handle_exit=handler,
        )
        failing = re.compile(r"FAIL: LLVM :: (.*) \(").findall(out)
        if len(failing) > 0:
            failing_tests.extend(failing)

    return failing_tests

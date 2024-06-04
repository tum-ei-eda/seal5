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
"""Seal5 dependencies."""

from typing import Optional
from pathlib import Path

import git

from seal5.logging import get_logger
from seal5.utils import is_populated

logger = get_logger()


class Dependency:
    pass


class GitDependency(Dependency):
    def __init__(self, name: str, clone_url: str, ref: Optional[str] = None, recursive: bool = False):
        self.name: str = name
        self.clone_url: str = clone_url
        self.ref: Optional[str] = ref
        self.recursive: bool = recursive

    def clone(self, dest: Path, overwrite: bool = False, depth: Optional[int] = None):
        if is_populated(dest):
            logger.debug("Updating repository: %s", dest)
            repo = git.Repo(dest)
            repo.remotes.origin.set_url(self.clone_url)
            repo.remotes.origin.fetch()
            repo.git.checkout(self.ref)
            repo.git.pull("origin", self.ref)
            return
        logger.debug("Cloning repository: %s", self.clone_url)
        repo = git.Repo.clone_from(
            self.clone_url, dest, recursive=self.recursive, no_checkout=self.ref is not None, depth=depth
        )
        if self.ref:
            logger.debug("Checking out: %s", self.ref)
            repo.git.checkout(self.ref)


class M2ISARDependency(GitDependency):
    # def __init__(self, clone_url="https://github.com/tum-ei-eda/M2-ISA-R.git", ref="coredsl_exceptions"):
    def __init__(self, clone_url="https://github.com/PhilippvK/M2-ISA-R-private.git", ref="seal5"):
        super().__init__("m2isar", clone_url, ref=ref)


class CDSL2LLVMDependency(GitDependency):
    # def __init__(self, clone_url="https://github.com/mathis-s/CoreDSL2LLVM.git", ref="main"):
    def __init__(self, clone_url="https://github.com/PhilippvK/CoreDSL2LLVM.git", ref="philippvk4"):
        super().__init__("cdsl2llvm", clone_url, ref=ref)


m2isar_dependency = M2ISARDependency()
cdsl2llvm_dependency = CDSL2LLVMDependency()

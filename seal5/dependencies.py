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


class Dependency:
    pass


class GitDependency(Dependency):

    def __init__(self, name: str, clone_url: str, ref: Optional[str] = None, recursive: bool = False):
        self.name: str = name
        self.clone_url: str = clone_url
        self.ref: Optional[str] = ref
        self.recursive: bool = recursive


class M2ISARDependency(GitDependency):

    def __init__(self, clone_url="TODO", ref="seal5"):
        super("m2isar", clone_url, ref=ref)


class CDSL2LLVMDependency(GitDependency):

    def __init__(self, clone_url="TODO", ref="seal5"):
        super("cdsl2llvm", clone_url, ref=ref)


m2isar_dependency = M2ISARDependency()
cdsl2llvm_dependency = CDSL2LLVMDependency()

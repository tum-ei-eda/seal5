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
"""Seal5 Flow API."""
from enum import Enum, auto
from pathlib import Path
from typing import Optional


class Seal5State(Enum):
    UNKNOWN = auto()
    UNINITIALIZED = auto()
    INITIALIZED = auto()



def handle_directory(directory: Optional[Path]):
    # TODO: handle environment vars
    if directory is None:
        assert NotImplementedError
    if not isinstance(directory, Path):
        path = Path(directory)
    return path


class Seal5Flow:

    def __init__(self, directory: Optional[Path] = None, name: str = "default"):
        self.directory: Path = directory
        self.name: str = name
        self.state: Seal5State = Seal5State.UNKNOWN
        self.check()

    def check(self):
        pass

    def initialize(self, interactive: bool = False, clone: bool = False, clone_url: Optional[str] = None, clone_ref: Optional[str] = None, force: bool = False):
        raise NotImplementedError

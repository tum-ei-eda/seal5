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
"""Utilities for handling Seal5 resources."""
import importlib_resources
from typing import Optional


# def get_patches(patch_name: str, target: Optional[str] = None, allow_missing: bool = False):
def get_patches(patch_name: Optional[str] = None, target: Optional[str] = None, allow_empty: bool = False):
    ret = []
    for entry in importlib_resources.files("seal5.resources.patches").iterdir():
        # print("entry", entry.name)
        if entry.is_dir():
            if target and target != entry.name:
                continue
            for entry2 in entry.iterdir():
                # print("entry2", entry2.name)
                assert not entry2.is_dir(), "Nested patches are not allowed"
                assert entry2.is_file(), f"Invalid patch: {entry.name}"
                if patch_name and patch_name not in entry2.stem:
                    continue
                ret.append(entry2.resolve())
        elif entry.is_file():
            ret.append(entry.resolve())

    if len(ret) == 0:
        assert allow_empty, "No patches found!"

    return ret


def get_test_cfg():
    ret = importlib_resources.files("seal5.resources").joinpath("lit.cfg.py")
    assert ret.is_file(), f"Test cfg not found: {ret}"
    return ret

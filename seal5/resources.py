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
import pkgutil
import os
import pkg_resources


def get_patch(target: str, patch_name: str):
    patch_files = pkg_resources.resource_listdir("seal5", os.path.join("..", "resources", "patches", target))
    patch_names = [x.split(".", 1)[0] for x in patch_files]
    assert patch_name in patch_names, f"Patch {patch_name} not found! Available: {patch_names}"
    patch_file = f"{name}.patch"
    return pkgutil.get_data("seal5", os.path.join("..", "resources", "patches", target, patch_file))

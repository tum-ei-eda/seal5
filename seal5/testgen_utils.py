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
"""Seal5 TestGen Utils."""


def collect_generated_test_files(index_file):
    import yaml

    with open(index_file, "r", encoding="utf-8") as file:
        index = yaml.safe_load(file)

    global_artifacts = index["artifacts"]
    ext_artifacts = sum([ext["artifacts"] for ext in index["extensions"]], [])
    all_artifacts = global_artifacts + ext_artifacts
    ret = []
    for artifact in all_artifacts:
        if artifact.get("is_test", False):
            dest_path = artifact["dest_path"]
            if dest_path.startswith("llvm/test/"):
                dest_path = dest_path.replace("llvm/test/", "")
            elif dest_path.startswith("./llvm/test/"):
                dest_path = dest_path.replace("./llvm/test/", "")
            ret.append(dest_path)
    return ret

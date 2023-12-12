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
"""Settings module for seal5."""
from pathlib import Path

import yaml

from seal5 import utils


class YAMLSettings:
    @staticmethod
    def from_yaml(text: str):
        data = yaml.safe_load(text)
        return Seal5Settings(data=data)

    @staticmethod
    def from_yaml_file(path: Path):
        with open(path, "r") as file:
            data = yaml.safe_load(file)
        return Seal5Settings(data=data)

    def __init__(self, data: dict = {}):
        self.data: dict = data
        assert self.validate()

    def to_yaml(self):
        data = self.data
        text = yaml.dump(data)
        return text

    def to_yaml_file(self, path: Path):
        text = self.to_yaml()
        with open(path, "w") as file:
            file.write(text)

    def validate(self):
        # TODO
        return True

    def merge(self, other: "YAMLSettings", overwrite: bool = False):
        # TODO:
        if overwrite:
            self.data.update(other.data)
        else:
            self.data = utils.merge_dicts(self.data, other.data)


class TestSettings(YAMLSettings):
    @property
    def paths(self):
        return self.data["paths"]


class PatchSettings(YAMLSettings):
    pass


class TransformSettings(YAMLSettings):
    pass


class ExtensionsSettings(YAMLSettings):
    pass


class GroupsSettings(YAMLSettings):
    pass


class LoggingSettings(YAMLSettings):
    @property
    def console(self):
        return self.data["console"]

    @property
    def file(self):
        return self.data["file"]


class FilterSettings(YAMLSettings):
    @property
    def sets(self):
        return self.data.get("sets")

    @property
    def instructions(self):
        return self.data.get("instructions")

    @property
    def aliases(self):
        return self.data.get("aliases")

    @property
    def intrinsics(self):
        return self.data.get("intrinsics")


class LLVMSettings(YAMLSettings):
    @property
    def state(self):
        return self.data["state"]

    @property
    def configs(self):
        return self.data["configs"]


class Seal5Settings(YAMLSettings):
    @property
    def logging(self):
        return LoggingSettings(data=self.data["logging"])

    @property
    def filter(self):
        return FilterSettings(data=self.data["filter"])

    @property
    def llvm(self):
        return LLVMSettings(data=self.data["llvm"])

    @property
    def patch(self):
        return PatchSettings(data=self.data["patch"])

    @property
    def transform(self):
        return TransformSettings(data=self.data["transform"])

    @property
    def test(self):
        return TestSettings(data=self.data["test"])

    @property
    def extensions(self):
        return ExtensionsSettings(data=self.data["extensions"])

    @property
    def groups(self):
        return GroupsSettings(data=self.data["groups"])

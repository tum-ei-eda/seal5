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
import logging
from pathlib import Path
from dataclasses import dataclass, field, asdict, fields
from typing import List, Union, Optional, Dict

import yaml
from dacite import from_dict

from seal5.types import PatchStage


DEFAULT_SETTINGS = {
    # "directory": ?,
    "logging": {
        "console": {
            "level": "INFO",
        },
        "file": {
            "level": "DEBUG",
            "rotate": False,
            "limit": 1000,
        },
    },
    "git": {
        "author": "Seal5",
        "mail": "example@example.com",
        "prefix": "[Seal5]",
    },
    "patches": [
        {
            "name": "gitignore",
            "file": "gitignore.patch",
            "target": "llvm",
            "stage": 0,
            "comment": "Add .seal5 directory to .gitignore",
        },
    ],
    "filter": {
        "sets": {
            "keep": [],
            "drop": [],
        },
        "instructions": {
            "keep": [],
            "drop": [],
        },
        "aliases": {
            "keep": [],
            "drop": [],
        },
        "intrinsics": {
            "keep": [],
            "drop": [],
        },
    },
    "transform": {
        "passes": "*",
    },
    "test": {
        "paths": ["MC/RISCV", "CodeGen/RISCV"],
    },
    "llvm": {
        "state": {"version": "auto", "base_commit": "unknown"},
        "configs": {
            "release": {
                "options": {
                    "CMAKE_BUILD_TYPE": "Release",
                    "LLVM_BUILD_TOOLS": True,
                    "LLVM_ENABLE_ASSERTIONS": False,
                    "LLVM_OPTIMIZED_TABLEGEN": True,
                    "LLVM_ENABLE_PROJECTS": ["clang", "lld"],
                    "LLVM_TARGETS_TO_BUILD": ["X86", "RISCV"],
                },
            },
            "release_assertions": {
                "options": {
                    "CMAKE_BUILD_TYPE": "Release",
                    "LLVM_BUILD_TOOLS": True,
                    "LLVM_ENABLE_ASSERTIONS": True,
                    "LLVM_OPTIMIZED_TABLEGEN": True,
                    "LLVM_ENABLE_PROJECTS": ["clang", "lld"],
                    "LLVM_TARGETS_TO_BUILD": ["X86", "RISCV"],
                },
            },
            "debug": {
                "options": {
                    "CMAKE_BUILD_TYPE": "Debug",
                    "LLVM_BUILD_TOOLS": True,
                    "LLVM_ENABLE_ASSERTIONS": True,
                    "LLVM_OPTIMIZED_TABLEGEN": True,
                    "LLVM_ENABLE_PROJECTS": ["clang", "lld"],
                    "LLVM_TARGETS_TO_BUILD": ["X86", "RISCV"],
                },
            },
        },
    },
    "inputs": [],
    "extensions": {
        # RV32Zpsfoperand:
        #   feature: RV32Zpsfoperand
        #   arch: rv32zpsfoperand
        #   version: "1.0"
        #   experimental: true
        #   vendor: false
        #   instructions/intrinsics/aliases/constraints: TODO
        #   # patches: []
    },
    "groups": {
        "all": "*",
    },
}


class YAMLSettings:
    @classmethod
    def from_dict(cls, data: dict):
        # print("from_dict", data)
        return from_dict(data_class=cls, data=data)

    @classmethod
    def from_yaml(cls, text: str):
        data = yaml.safe_load(text)
        return cls.from_dict(data)

    @classmethod
    def from_yaml_file(cls, path: Path):
        with open(path, "r") as file:
            data = yaml.safe_load(file)
        return cls.from_dict(data=data)

    def to_yaml(self):
        data = asdict(self)
        text = yaml.dump(data)
        return text

    def to_yaml_file(self, path: Path):
        text = self.to_yaml()
        with open(path, "w") as file:
            file.write(text)

    def merge(self, other: "YAMLSettings", overwrite: bool = False):
        # print("merge", type(self), type(other))
        for f1 in fields(other):
            k1 = f1.name
            # if k1 == "prefix":
            #     input("1 PREFIX")
            v1 = getattr(other, k1)
            if v1 is None:
                # print("cont1")
                continue
            t1 = type(v1)
            # print("f1", f1.name, f1, type(f1))
            # print("other", k1, v1)
            found = False
            for f2 in fields(self):
                k2 = f2.name
                # if k2 == "prefix":
                #     print("f1", f1)
                #     print("f2", f2)
                #     input("2 PREFIX")
                v2 = getattr(self, k2)
                if k2 == k1:
                    found = True
                    if v2 is not None:
                        t2 = type(v2)
                        assert t1 is t2, "Type conflict"
                        if isinstance(v1, YAMLSettings):
                            v2.merge(v1, overwrite=overwrite)
                        elif isinstance(v1, dict):
                            if overwrite:
                                v2.clear()
                            v2.update(v1)
                        elif isinstance(v1, list):
                            if overwrite:
                                v2.clear()
                            v2.extend(v1)
                        else:
                            assert isinstance(
                                v2, (int, float, str, bool, Path)
                            ), f"Unsupported field type for merge {t1}"
                            setattr(self, k1, v1)
                    break
                # print("f2", f2.name, f2, type(f2))
                # print("self", k2, v2)
            assert found

        # input("123")
        # if overwrite:
        #     self.data.update(other.data)
        # else:
        #     # self.data = utils.merge_dicts(self.data, other.data)

    # @staticmethod
    # def from_yaml(text: str):
    #     data = yaml.safe_load(text)
    #     return Seal5Settings(data=data)

    # @staticmethod
    # def from_yaml_file(path: Path):
    #     with open(path, "r") as file:
    #         data = yaml.safe_load(file)
    #     return Seal5Settings(data=data)

    # # def __init__(self, data: dict = {}):
    # #     self.data: dict = data
    # #     assert self.validate()

    # def to_yaml(self):
    #     data = self.data
    #     text = yaml.dump(data)
    #     return text

    # def to_yaml_file(self, path: Path):
    #     text = self.to_yaml()
    #     with open(path, "w") as file:
    #         file.write(text)

    # def validate(self):
    #     # TODO
    #     return True

    # def merge(self, other: "YAMLSettings", overwrite: bool = False):
    #     # TODO:
    #     if overwrite:
    #         self.data.update(other.data)
    #     else:
    #         self.data = utils.merge_dicts(self.data, other.data)


@dataclass
class TestSettings(YAMLSettings):
    paths: Optional[List[Union[Path, str]]] = None


@dataclass
class GitSettings(YAMLSettings):
    author: str = "Seal5"
    mail: str = "example@example.com"
    prefix: Optional[str] = "[Seal5]"


@dataclass
class PatchSettings(YAMLSettings):
    name: str
    target: Optional[str] = None
    stage: Optional[Union[PatchStage, int]] = None  # TODO: default to 0? Allow int with union?
    comment: Optional["str"] = None
    file: Optional[Union[Path, str]] = None
    # _file: Optional[Union[Path, str]] = field(init=False, repr=False)
    enable: bool = True

    # @property
    # def file(self) -> Path:
    #     return self._file

    # @file.setter
    # def file(self, value: Optional[Union[Path, str]]):
    #     self._file = value


@dataclass
class TransformSettings(YAMLSettings):
    pass


@dataclass
class ExtensionsSettings(YAMLSettings):
    feature: Optional[str] = None
    arch: Optional[str] = None
    version: Optional[str] = None
    experimental: Optional[bool] = None
    vendor: Optional[bool] = None
    model: Optional[str] = None
    instructions: Optional[List[str]] = None
    # patches


@dataclass
class GroupsSettings(YAMLSettings):
    pass


@dataclass
class ConsoleLoggingSettings(YAMLSettings):
    level: Union[int, str] = logging.INFO


@dataclass
class FileLoggingSettings(YAMLSettings):
    level: Union[int, str] = logging.INFO
    limit: Optional[int] = None  # TODO: implement
    rotate: bool = False  # TODO: implement


@dataclass
class LoggingSettings(YAMLSettings):
    console: ConsoleLoggingSettings
    file: FileLoggingSettings


@dataclass
class FilterSetting(YAMLSettings):
    keep: List[str] = field(default_factory=list)
    drop: List[str] = field(default_factory=list)


@dataclass
class FilterSettings(YAMLSettings):
    sets: Optional[FilterSetting] = None
    instructions: Optional[FilterSetting] = None
    aliases: Optional[FilterSetting] = None
    intrinsics: Optional[FilterSetting] = None
    # TODO: functions


@dataclass
class LLVMState(YAMLSettings):
    base_commit: Optional[str] = None
    version: Optional[str] = None


@dataclass
class LLVMConfig(YAMLSettings):
    options: dict = field(default_factory=dict)


@dataclass
class LLVMSettings(YAMLSettings):
    state: Optional[LLVMState] = None
    configs: Optional[Dict[str, LLVMConfig]] = None


@dataclass
class Seal5Settings(YAMLSettings):
    logging: Optional[LoggingSettings] = None
    filter: Optional[FilterSettings] = None
    llvm: Optional[LLVMSettings] = None
    git: Optional[GitSettings] = None
    patches: Optional[List[PatchSettings]] = None
    transform: Optional[TransformSettings] = None  # TODO: make list?
    test: Optional[TestSettings] = None
    extensions: Optional[Dict[str, ExtensionsSettings]] = None
    groups: Optional[GroupsSettings] = None  # TODO: make list?
    inputs: Optional[List[str]] = None

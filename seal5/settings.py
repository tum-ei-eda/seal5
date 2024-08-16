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
    "name": "default",
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
        "opcodes": {
            "keep": [],
            "drop": [],
        },
        "encoding_sizes": {
            "keep": [],
            "drop": [],
        },
    },
    # "transform": {
    #     "passes": "*",
    # },
    "passes": {
        "defaults": {
            "skip": [],
            "only": [],
            "overrides": {},
        },
        "per_model": {},
    },
    "test": {
        "paths": [],
        # "paths": ["MC/RISCV", "CodeGen/RISCV"],
    },
    "llvm": {
        "state": {"version": "auto", "base_commit": "unknown"},
        "ninja": True,
        "default_config": "release",
        "clone_depth": None,
        "configs": {
            "release": {
                "options": {
                    "CMAKE_BUILD_TYPE": "Release",
                    "LLVM_BUILD_TOOLS": True,
                    "LLVM_ENABLE_ASSERTIONS": False,
                    "LLVM_OPTIMIZED_TABLEGEN": True,
                    "LLVM_ENABLE_PROJECTS": ["clang", "lld"],
                    "LLVM_TARGETS_TO_BUILD": ["RISCV"],
                },
            },
            "release_assertions": {
                "options": {
                    "CMAKE_BUILD_TYPE": "Release",
                    "LLVM_BUILD_TOOLS": True,
                    "LLVM_ENABLE_ASSERTIONS": True,
                    "LLVM_OPTIMIZED_TABLEGEN": True,
                    "LLVM_ENABLE_PROJECTS": ["clang", "lld"],
                    "LLVM_TARGETS_TO_BUILD": ["RISCV"],
                },
            },
            "debug": {
                "options": {
                    "CMAKE_BUILD_TYPE": "Debug",
                    "LLVM_BUILD_TOOLS": True,
                    "LLVM_ENABLE_ASSERTIONS": True,
                    "LLVM_OPTIMIZED_TABLEGEN": True,
                    "LLVM_ENABLE_PROJECTS": ["clang", "lld"],
                    "LLVM_TARGETS_TO_BUILD": ["RISCV"],
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
    "tools": {
        "pattern_gen": {
            "integrated": True,
            "clone_url": None,
            "ref": None,
            # "clone_depth": None,
            "clone_depth": 1,
            "sparse_checkout": True,
        },
    },
}


def check_supported_types(data):
    ALLOWED_TYPES = (int, float, str, bool)
    if isinstance(data, dict):
        for value in data.values():
            check_supported_types(value)
    elif isinstance(data, list):
        for x in data:
            check_supported_types(x)
    else:
        if data is not None:
            assert isinstance(data, ALLOWED_TYPES), f"Unsupported type: {type(data)}"


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
        check_supported_types(data)
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
                    if v2 is None:
                        setattr(self, k2, v1)
                    else:
                        t2 = type(v2)
                        assert t1 is t2, "Type conflict"
                        if isinstance(v1, YAMLSettings):
                            v2.merge(v1, overwrite=overwrite)
                        elif isinstance(v1, dict):
                            if overwrite:
                                v2.clear()
                                v2.update(v1)
                            else:
                                for dict_key, dict_val in v1.items():
                                    if dict_key in v2:
                                        if isinstance(dict_val, YAMLSettings):
                                            assert isinstance(v2[dict_key], YAMLSettings)
                                            v2[dict_key].merge(dict_val, overwrite=overwrite)
                                    else:
                                        v2[dict_key] = dict_val
                        elif isinstance(v1, list):
                            if overwrite:
                                v2.clear()
                            # duplicates are dropped here
                            new = [x for x in v1 if x not in v2]
                            v2.extend(new)
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
    index: Optional[Union[Path, str]] = None
    # _file: Optional[Union[Path, str]] = field(init=False, repr=False)
    enable: bool = True
    generated: bool = False
    applied: bool = False

    # @property
    # def file(self) -> Path:
    #     return self._file

    # @file.setter
    # def file(self, value: Optional[Union[Path, str]]):
    #     self._file = value


# @dataclass
# class TransformSettings(YAMLSettings):
#     pass


@dataclass
class PassesSetting(YAMLSettings):
    skip: Optional[List[str]] = None
    only: Optional[List[str]] = None
    overrides: Optional[dict] = None


@dataclass
class PassesSettings(YAMLSettings):
    defaults: Optional[PassesSetting] = None
    per_model: Optional[Dict[str, PassesSetting]] = None


@dataclass
class ExtensionsSettings(YAMLSettings):
    feature: Optional[str] = None
    predicate: Optional[str] = None
    arch: Optional[str] = None
    version: Optional[str] = None
    experimental: Optional[bool] = None
    vendor: Optional[bool] = None
    std: Optional[bool] = None
    model: Optional[str] = None
    description: Optional[str] = None
    requires: Optional[List[str]] = None
    instructions: Optional[List[str]] = None
    # patches

    def get_version(self):
        if self.version:
            return self.version
        else:
            return "1.0"

    def get_description(self, name: Optional[str] = None):
        if self.description is None:
            if name:
                description = name
            else:
                description = "RISC-V"
            description += " Extension"
            return description
        else:
            return self.description

    def get_arch(self, name: Optional[str] = None):
        if self.arch is None:
            feature = self.get_feature(name=name)
            assert feature is not None
            arch = feature.lower()
            if self.experimental:
                arch = "experimental-" + arch
            return arch
        return self.arch

    def get_feature(self, name: Optional[str] = None):
        if self.feature is None:
            assert name is not None
            feature = name.replace("_", "")
            return feature
        else:
            return self.feature

    def get_predicate(self, name: Optional[str] = None, with_has: bool = False):
        if self.predicate is None:
            feature = self.get_feature(name=name)
            assert feature is not None
            if self.vendor:
                assert not self.std
                prefix = "Vendor"
            elif self.std:
                prefix = "StdExt"
            else:
                prefix = "Ext"
            if with_has:
                prefix = "Has" + prefix
            return prefix + feature
        else:
            if with_has:
                assert "has" in self.predicate.lower()
            return self.predicate


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
    keep: List[Union[str, int]] = field(default_factory=list)
    drop: List[Union[str, int]] = field(default_factory=list)


@dataclass
class FilterSettings(YAMLSettings):
    sets: Optional[FilterSetting] = None
    instructions: Optional[FilterSetting] = None
    aliases: Optional[FilterSetting] = None
    intrinsics: Optional[FilterSetting] = None
    opcodes: Optional[FilterSetting] = None
    encoding_sizes: Optional[FilterSetting] = None
    # TODO: functions


@dataclass
class LLVMVersion(YAMLSettings):
    major: Optional[int] = None
    minor: Optional[int] = None
    patch: Optional[int] = None
    rc: Optional[int] = None


@dataclass
class LLVMState(YAMLSettings):
    base_commit: Optional[str] = None
    version: Optional[Union[str, LLVMVersion]] = None


@dataclass
class LLVMConfig(YAMLSettings):
    options: dict = field(default_factory=dict)


@dataclass
class LLVMSettings(YAMLSettings):
    ninja: Optional[bool] = None
    clone_depth: Optional[int] = None
    default_config: Optional[str] = None
    configs: Optional[Dict[str, LLVMConfig]] = None
    state: Optional[LLVMState] = None


@dataclass
class RISCVLegalizerSetting(YAMLSettings):
    name: Optional[Union[str, List[str]]] = None
    types: Optional[Union[str, List[str]]] = None
    onlyif: Optional[Union[str, List[str]]] = None


@dataclass
class RISCVLegalizerSettings(YAMLSettings):
    ops: Optional[List[RISCVLegalizerSetting]] = None


@dataclass
class RISCVSettings(YAMLSettings):
    xlen: Optional[int] = None
    features: Optional[List[str]] = None
    # Used for  baseline extensions, tune and legalizer + pattern gen
    # default: zicsr,m,(32/64bit),fast-unaligned-access
    # others: zmmul,a,f,d,zfh,zfinx,zdinx,c,zba,zbb,zbc,zbs,zca,zcb,zcd
    #   zcmp,zce,e,no-optimized-zero-stride-load,no-default-unroll,...
    transform_info: Optional[Dict[str, Optional[Union[bool, int]]]] = None
    # options: see ttiimpl_notes.txt
    # TODO: processor/pipeline/mcpu/tune -> ProcessorSettings
    legalization: Optional[Dict[str, RISCVLegalizerSettings]] = None


@dataclass
class PatternGenSettings(YAMLSettings):
    integrated: Optional[bool] = None
    clone_url: Optional[str] = None
    ref: Optional[str] = None
    clone_depth: Optional[int] = None
    sparse_checkout: Optional[bool] = None


@dataclass
class ToolsSettings(YAMLSettings):
    pattern_gen: Optional[PatternGenSettings] = None


@dataclass
class Seal5Settings(YAMLSettings):
    directory: Optional[str] = None
    name: Optional[str] = None
    meta_dir: Optional[str] = None
    logging: Optional[LoggingSettings] = None
    filter: Optional[FilterSettings] = None
    llvm: Optional[LLVMSettings] = None
    git: Optional[GitSettings] = None
    patches: Optional[List[PatchSettings]] = None
    # transform: Optional[TransformSettings] = None  # TODO: make list?
    passes: Optional[PassesSettings] = None  # TODO: make list?
    test: Optional[TestSettings] = None
    extensions: Optional[Dict[str, ExtensionsSettings]] = None
    groups: Optional[GroupsSettings] = None  # TODO: make list?
    inputs: Optional[List[str]] = None
    riscv: Optional[RISCVSettings] = None
    tools: Optional[ToolsSettings] = None
    metrics: list = field(default_factory=list)

    def reset(self):
        self.extensions = {}
        self.patches = []
        self.name = "default"
        self.inputs = []
        self.metrics = []
        self.test = TestSettings(paths=[])
        self.filter = FilterSettings(
            sets=FilterSetting(keep=[], drop=[]),
            instructions=FilterSetting(keep=[], drop=[]),
            aliases=FilterSetting(keep=[], drop=[]),
            intrinsics=FilterSetting(keep=[], drop=[]),
            opcodes=FilterSetting(keep=[], drop=[]),
            encoding_sizes=FilterSetting(keep=[], drop=[]),
        )
        self.passes = PassesSettings(
            defaults=PassesSetting(
                skip=[],
                only=[],
                overrides={},
            ),
            per_model={},
        )
        self.riscv = RISCVSettings(
            xlen=None,
            features=None,
            transform_info=None,
            legalization=None,
        )

    def save(self, dest: Optional[Path] = None):
        if dest is None:
            dest = self.settings_file
        self.to_yaml_file(dest)

    def add_patch(self, patch_settings: PatchSettings):
        for ps in self.patches:
            if ps.name == patch_settings.name:
                raise RuntimeError(f"Duplicate patch '{ps.name}'. Either clean patches or rename patch.")
        self.patches.append(patch_settings)

    @property
    def model_names(self):
        return [Path(path).stem for path in self.inputs]

    @property
    def _meta_dir(self):
        return Path(self.meta_dir)

    @property
    def settings_file(self):
        return self._meta_dir / "settings.yml"

    @property
    def deps_dir(self):
        return self._meta_dir / "deps"

    @property
    def build_dir(self):
        return self._meta_dir / "build"

    @property
    def install_dir(self):
        return self._meta_dir / "install"

    @property
    def logs_dir(self):
        return self._meta_dir / "logs"

    @property
    def models_dir(self):
        return self._meta_dir / "models"

    @property
    def inputs_dir(self):
        return self._meta_dir / "inputs"

    @property
    def temp_dir(self):
        return self._meta_dir / "temp"

    @property
    def gen_dir(self):
        return self._meta_dir / "gen"

    @property
    def tests_dir(self):
        return self._meta_dir / "tests"

    @property
    def patches_dir(self):  # TODO: maybe merge with gen_dir
        return self._meta_dir / "patches"

    @property
    def log_file_path(self):
        return self.logs_dir / "seal5.log"

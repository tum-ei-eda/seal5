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
from dataclasses import dataclass, field, asdict, fields, replace
from typing import List, Union, Optional, Dict

import yaml
import dacite
from dacite import from_dict, Config

from seal5.types import PatchStage
from seal5.utils import parse_cond
from seal5.logging import get_logger

logger = get_logger()


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
        "skip": [],
        "only": [],
        "overrides": {},
    },
    "test": {
        "paths": [],
        # "paths": ["MC/RISCV", "CodeGen/RISCV"],
    },
    "llvm": {
        "state": {"version": "auto", "base_commit": "unknown", "supported_imm_types": []},
        "ninja": True,
        "ccache": {
            "enable": False,
            "executable": "auto",
            "directory": None,
        },
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
    "models": {},
    # "groups": {
    #     "all": "*",
    # },
    "tools": {
        "pattern_gen": {
            "integrated": True,
            "clone_url": None,
            "ref": None,
            # "clone_depth": None,
            "clone_depth": 1,
            "sparse_checkout": False,
        },
    },
    "intrinsics": {},
}


ALLOWED_YAML_TYPES = (int, float, str, bool)


def check_supported_types(data):
    """Assert that now unsupported types are written into YAML file."""
    if isinstance(data, dict):
        for value in data.values():
            check_supported_types(value)
    elif isinstance(data, list):
        for x in data:
            check_supported_types(x)
    else:
        if data is not None:
            assert isinstance(data, ALLOWED_YAML_TYPES), f"Unsupported type: {type(data)}"


class YAMLSettings:  # TODO: make abstract
    """Generic YAMLSettings."""

    @classmethod
    def from_dict(cls, data: dict):
        """Convert dict into instance of YAMLSettings."""
        try:
            return from_dict(data_class=cls, data=data, config=Config(strict=True))
        except dacite.exceptions.UnexpectedDataError as err:
            logger.error("Unexpected key in Seal5Settings. Check for missmatch between Seal5 versions!")
            raise err

    @classmethod
    def from_yaml(cls, text: str):
        """Write settings to YAML file."""
        data = yaml.safe_load(text)
        return cls.from_dict(data)

    @classmethod
    def from_yaml_file(cls, path: Path):
        """Parse settings from YAML file."""
        with open(path, "r", encoding="utf-8") as file:
            data = yaml.safe_load(file)
        return cls.from_dict(data)

    def to_yaml(self):
        """Convert settings to YAML string."""
        data = asdict(self)
        check_supported_types(data)
        text = yaml.dump(data)
        return text

    def to_yaml_file(self, path: Path):
        """Write settings to YAML file."""
        text = self.to_yaml()
        with open(path, "w", encoding="utf-8") as file:
            file.write(text)

    def merge(self, other: "YAMLSettings", overwrite: bool = False, inplace: bool = False):
        """Merge two instances of YAMLSettings."""
        if not inplace:
            ret = replace(self)  # Make a copy of self
        for f1 in fields(other):
            k1 = f1.name
            v1 = getattr(other, k1)
            if v1 is None:
                continue
            t1 = type(v1)
            found = False
            for f2 in fields(self):
                k2 = f2.name
                v2 = getattr(self, k2)
                if k2 == k1:
                    found = True
                    if v2 is None:
                        if inplace:
                            setattr(self, k2, v1)
                        else:
                            setattr(ret, k2, v1)
                    else:
                        t2 = type(v2)
                        assert t1 is t2, "Type conflict"
                        if isinstance(v1, YAMLSettings):
                            v2.merge(v1, overwrite=overwrite, inplace=True)
                        elif isinstance(v1, dict):
                            if overwrite:
                                v2.clear()
                                v2.update(v1)
                            else:
                                for dict_key, dict_val in v1.items():
                                    if dict_key in v2:
                                        if isinstance(dict_val, YAMLSettings):
                                            assert isinstance(v2[dict_key], YAMLSettings)
                                            v2[dict_key].merge(dict_val, overwrite=overwrite, inplace=True)
                                        elif isinstance(dict_val, dict):
                                            v2[dict_key].update(dict_val)
                                        else:
                                            v2[dict_key] = dict_val
                                    else:
                                        v2[dict_key] = dict_val
                        elif isinstance(v1, list):
                            if overwrite:
                                v2.clear()
                            new = [x for x in v1 if x not in v2]
                            v2.extend(new)
                        else:
                            assert isinstance(
                                v2, (int, float, str, bool, Path)
                            ), f"Unsupported field type for merge {t1}"
                            if inplace:
                                setattr(self, k1, v1)
                            else:
                                setattr(ret, k1, v1)
                    break
            assert found
        if not inplace:
            return ret

        # input("123")
        # if overwrite:
        #     ret.data.update(other.data)
        # else:
        #     # ret.data = utils.merge_dicts(ret.data, other.data)

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
    """Seal5 test settings."""

    paths: Optional[List[Union[Path, str]]] = None


@dataclass
class GitSettings(YAMLSettings):
    """Seal5 git settings."""

    author: str = "Seal5"
    mail: str = "example@example.com"
    prefix: Optional[str] = "[Seal5]"


@dataclass
class PatchSettings(YAMLSettings):
    """Seal5 patch settings."""

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
    onlyif: Optional[str] = None

    def check_enabled(self, settings: YAMLSettings):
        if self.onlyif is not None:
            if isinstance(self.onlyif, str):
                res = parse_cond(self.onlyif, settings)
            elif isinstance(self.onlyif, int):
                res = bool(res)
            assert isinstance(res, bool)
            return res
        return self.enable

    # @property
    # def file(self) -> Path:
    #     return self._file

    # @file.setter
    # def file(self, value: Optional[Union[Path, str]]):
    #     self._file = value


# @dataclass
# class TransformSettings(YAMLSettings):
#     pass


# @dataclass
# class PassesSetting(YAMLSettings):
#     """Seal5 model-specific passes settings."""
#
#     skip: Optional[List[str]] = None
#     only: Optional[List[str]] = None
#     overrides: Optional[dict] = None
#
#
# @dataclass
# class PassesSettings(YAMLSettings):
#     """Seal5 passes settings."""
#
#     defaults: Optional[PassesSetting] = None
#     per_model: Optional[Dict[str, PassesSetting]] = None


@dataclass
class PassesSettings(YAMLSettings):
    """Seal5 model-specific passes settings."""

    skip: Optional[List[str]] = None
    only: Optional[List[str]] = None
    overrides: Optional[dict] = None


@dataclass
class ConsoleLoggingSettings(YAMLSettings):
    """Seal5 console logging settings."""

    level: Union[int, str] = logging.INFO


@dataclass
class FileLoggingSettings(YAMLSettings):
    """Seal5 file logging settings."""

    level: Union[int, str] = logging.INFO
    limit: Optional[int] = None  # TODO: implement
    rotate: bool = False  # TODO: implement


@dataclass
class LoggingSettings(YAMLSettings):
    """Seal5 logging settings."""

    console: ConsoleLoggingSettings
    file: FileLoggingSettings


@dataclass
class FilterSetting(YAMLSettings):
    """Seal5 set/instr/alias/instrinsic/opcode/enc-specific filter settings."""

    keep: List[Union[str, int]] = field(default_factory=list)
    drop: List[Union[str, int]] = field(default_factory=list)


@dataclass
class FilterSettings(YAMLSettings):
    """Seal5 filter settings."""

    sets: Optional[FilterSetting] = None
    instructions: Optional[FilterSetting] = None
    aliases: Optional[FilterSetting] = None
    intrinsics: Optional[FilterSetting] = None
    opcodes: Optional[FilterSetting] = None
    encoding_sizes: Optional[FilterSetting] = None
    # TODO: functions


@dataclass
class LLVMVersion(YAMLSettings):
    """Seal5 llvm version settings."""

    major: Optional[int] = None
    minor: Optional[int] = None
    patch: Optional[int] = None
    rc: Optional[int] = None

    @property
    def triple(self):
        return (self.major, self.minor, self.patch)


@dataclass
class LLVMState(YAMLSettings):
    """Seal5 llvm state settings."""

    base_commit: Optional[str] = None
    version: Optional[Union[str, LLVMVersion]] = None
    supported_imm_types: Optional[List[str]] = None


@dataclass
class LLVMConfig(YAMLSettings):
    """Seal5 llvm config settings."""

    options: dict = field(default_factory=dict)


@dataclass
class CcacheSettings(YAMLSettings):
    """Seal5 ccache settings."""

    enable: Optional[bool] = None
    executable: Optional[str] = None
    directory: Optional[str] = None


@dataclass
class LLVMSettings(YAMLSettings):
    """Seal5 llvm settings."""

    ninja: Optional[bool] = None
    ccache: Optional[CcacheSettings] = None
    clone_depth: Optional[int] = None
    default_config: Optional[str] = None
    configs: Optional[Dict[str, LLVMConfig]] = None
    state: Optional[LLVMState] = None


@dataclass
class RISCVLegalizerSetting(YAMLSettings):
    """Seal5 riscv legalizer single settings."""

    name: Optional[Union[str, List[str]]] = None
    types: Optional[Union[str, List[str]]] = None
    onlyif: Optional[Union[str, List[str]]] = None


@dataclass
class RISCVLegalizerSettings(YAMLSettings):
    """Seal5 riscv legalizer settings."""

    ops: Optional[List[RISCVLegalizerSetting]] = None


@dataclass
class RISCVSettings(YAMLSettings):
    """Seal5 riscv settings."""

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
class ExtensionsSettings(YAMLSettings):
    """Seal5 extensions settings."""

    feature: Optional[str] = None
    predicate: Optional[str] = None
    arch: Optional[str] = None
    version: Optional[str] = None
    experimental: Optional[bool] = None
    vendor: Optional[bool] = None
    description: Optional[str] = None
    requires: Optional[List[str]] = None
    instructions: Optional[List[str]] = None
    riscv: Optional[RISCVSettings] = None
    passes: Optional[PassesSettings] = None
    required_imm_types: Optional[List[str]] = None
    # patches

    def get_version(self):
        """Get extension version."""
        if self.version:
            return self.version
        return "1.0"

    def get_description(self, name: Optional[str] = None):
        """Get extension description."""
        if self.description is None:
            if name:
                description = name
            else:
                description = "RISC-V"
            description += " Extension"
            return description
        return self.description

    def get_arch(self, name: Optional[str] = None):
        """Get extension arch."""
        arch = self.arch
        if arch is None:
            feature = self.get_feature(name=name)
            assert feature is not None
            arch = feature.lower()
            assert len(arch) > 1
            if arch[0] != "x":
                arch = f"x{arch}"
            # if self.experimental:
            #     arch = "experimental-" + arch
        assert arch[0] in ["z", "x"], "Arch needs to be start with z/x"
        return arch

    def get_feature(self, name: Optional[str] = None):
        """Get extension feature."""
        if self.feature is None:
            assert name is not None
            feature = name.replace("_", "")
            assert len(feature) > 1
            if feature.lower()[0] != "x":
                feature = f"X{feature}"
            return feature
        return self.feature

    def get_predicate(self, name: Optional[str] = None, with_has: bool = False):
        """Get extension predicate."""
        if self.predicate is None:
            feature = self.get_feature(name=name)
            assert feature is not None
            if self.vendor:
                prefix = "Vendor"
            else:
                prefix = "StdExt"
            if with_has:
                prefix = "Has" + prefix
            return prefix + feature
        if with_has:
            assert "has" in self.predicate.lower()
        return self.predicate


@dataclass
class ModelSettings(YAMLSettings):
    """Seal5 model settings."""

    extensions: Optional[Dict[str, ExtensionsSettings]] = None
    riscv: Optional[RISCVSettings] = None
    passes: Optional[PassesSettings] = None


@dataclass
class PatternGenSettings(YAMLSettings):
    """Seal5 pattern-gen settings."""

    integrated: Optional[bool] = None
    clone_url: Optional[str] = None
    ref: Optional[str] = None
    clone_depth: Optional[int] = None
    sparse_checkout: Optional[bool] = None


@dataclass
class ToolsSettings(YAMLSettings):
    """Seal5 tools settings."""

    pattern_gen: Optional[PatternGenSettings] = None


@dataclass
class IntrinsicArg(YAMLSettings):
    arg_name: str
    arg_type: str
    immediate: bool = False
    signed: bool = False


@dataclass
class IntrinsicDefn(YAMLSettings):
    instr_name: str
    intrinsic_name: str
    set_name: Optional[str] = None
    ret_type: Optional[str] = None
    ret_signed: Optional[bool] = None
    args: Optional[List[IntrinsicArg]] = None


@dataclass
class IntrinsicsSettings(YAMLSettings):
    intrinsics: Optional[List[IntrinsicDefn]] = None


@dataclass
class Seal5Settings(YAMLSettings):
    """Seal5 settings."""

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
    models: Optional[Dict[str, ModelSettings]] = None
    # groups: Optional[GroupsSettings] = None  # TODO: make list?
    inputs: Optional[List[str]] = None
    riscv: Optional[RISCVSettings] = None
    tools: Optional[ToolsSettings] = None
    metrics: list = field(default_factory=list)
    intrinsics: Optional[IntrinsicsSettings] = None

    def reset(self):
        """Reset Seal5 seetings."""
        self.models = {}
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
            skip=[],
            only=[],
            overrides={},
        )
        self.riscv = RISCVSettings(
            xlen=None,
            features=None,
            transform_info=None,
            legalization=None,
        )
        self.intrinsics = IntrinsicsSettings()

    def save(self, dest: Optional[Path] = None):
        """Save Seal5 settings to file."""
        if dest is None:
            dest = self.settings_file
        self.to_yaml_file(dest)

    def add_patch(self, patch_settings: PatchSettings):
        """Add patch to Seal5 seetings."""
        for ps in self.patches:
            if ps.name == patch_settings.name:
                raise RuntimeError(f"Duplicate patch '{ps.name}'. Either clean patches or rename patch.")
        self.patches.append(patch_settings)

    @property
    def model_names(self):
        """Seal5 model_names getter."""
        return [Path(path).stem for path in self.inputs]

    @property
    def _meta_dir(self):
        """Seal5 _meta_dir getter."""
        return Path(self.meta_dir)

    @property
    def settings_file(self):
        """Seal5 settings_file getter."""
        return self._meta_dir / "settings.yml"

    @property
    def deps_dir(self):
        """Seal5 deps_dir getter."""
        return self._meta_dir / "deps"

    @property
    def build_dir(self):
        """Seal5 build_dir getter."""
        return self._meta_dir / "build"

    def get_llvm_build_dir(self, config: Optional[str] = None, fallback: bool = True, check: bool = False):
        if config is None:
            # check if default_exists
            assert self.llvm is not None
            config = self.llvm.default_config

        assert config is not None, "Could not resolve LLVM build dir"

        llvm_build_dir = self.build_dir / config

        if not llvm_build_dir.is_dir():
            assert fallback, f"LLVM build dir {llvm_build_dir} does not exist and fallback is disabled."
            # Look for non-empty subdirs for .seal5/build
            candidates = [f for f in self.build_dir.iterdir() if f.is_dir() and any(f.iterdir())]
            if len(candidates) > 0:
                llvm_build_dir = candidates[0]
        if check:
            assert llvm_build_dir.is_dir(), f"LLVM build dir does not exist: {llvm_build_dir}"
        return llvm_build_dir

    @property
    def install_dir(self):
        """Seal5 install_dir getter."""
        return self._meta_dir / "install"

    @property
    def logs_dir(self):
        """Seal5 logs_dir getter."""
        return self._meta_dir / "logs"

    @property
    def models_dir(self):
        """Seal5 models_dir getter."""
        return self._meta_dir / "models"

    @property
    def inputs_dir(self):
        """Seal5 inputs_dir getter."""
        return self._meta_dir / "inputs"

    @property
    def temp_dir(self):
        """Seal5 temp_dir getter."""
        return self._meta_dir / "temp"

    @property
    def gen_dir(self):
        """Seal5 gen_dir getter."""
        return self._meta_dir / "gen"

    @property
    def tests_dir(self):
        """Seal5 tests_dir getter."""
        return self._meta_dir / "tests"

    @property
    def patches_dir(self):  # TODO: maybe merge with gen_dir
        """Seal5 patches_dir getter."""
        return self._meta_dir / "patches"

    @property
    def log_file_path(self):
        """Seal5 log_file_path getter."""
        return self.logs_dir / "seal5.log"

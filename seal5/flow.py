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
from typing import Optional, List

import git

from seal5.logging import get_logger
from seal5.dependencies import m2isar_dependency, cdsl2llvm_dependency
from seal5 import utils

logger = get_logger()


def get_cmake_args(cfg: dict):
    ret = []
    for key, value in cfg.items():
        if isinstance(value, bool):
            value = "ON" if value else "OFF"
        elif isinstance(value, list):
            value = ";".join(value)
        else:
            assert isinstance(value, (int, str)), "Unsupported cmake cfg"
        ret.append(f"-D{key}={value}")
    return ret


def build_llvm(src: Path, dest: Path, debug: bool = False, use_ninja: bool = False):
    cmake_cfg = {
        "LLVM_ENABLE_PROJECTS": ["clang", "lld"],
        "LLVM_TARGETS_TO_BUILD": ["X86", "RISCV"],
        "LLVM_OPTIMIZED_TABLEGEN": True,
        "LLVM_ENABLE_ASSERTIONS": debug,
        "LLVM_PARALLEL_LINK_JOBS": 16,  # TODO: make this dynamic!
        "LLVM_BUILD_TOOLS": True,
    }
    cmake_args = get_cmake_args(cmake_cfg)
    dest.mkdir(exist_ok=True)
    utils.cmake(src / "llvm", *cmake_args, debug=debug, use_ninja=use_ninja, cwd=dest)
    utils.make(cwd=dest)


class Seal5State(Enum):
    UNKNOWN = auto()
    UNINITIALIZED = auto()
    INITIALIZED = auto()


class Seal5Config:
    pass

def handle_directory(directory: Optional[Path]):
    # TODO: handle environment vars
    if directory is None:
        assert NotImplementedError
    if not isinstance(directory, Path):
        path = Path(directory)
    return path


def create_seal5_directories(path: Path, directories: list):
    logger.debug("Creating Seal5 directories")
    if not isinstance(path, Path):
        path = Path(path)
    if not path.is_dir():
        raise RuntimeError(f"Not a diretory: {path}")
    for directory in directories:
        (path / directory).mkdir(parents=True, exist_ok=True)


def clone_llvm_repo(
    dest: Path, clone_url: str, ref: Optional[str] = None
):  # TODO: how to get submodule url/ref
    logger.debug("Cloning LLVM repository: %s", clone_url)
    repo = git.Repo.clone_from(clone_url, dest, no_checkout=ref is not None)
    if ref:
        logger.debug("Checking out branch: %s", ref)
        repo.git.checkout(ref)


class Seal5Flow:
    def __init__(self, directory: Optional[Path] = None, name: str = "default"):
        self.directory: Path = handle_directory(directory)
        self.name: str = name
        self.state: Seal5State = Seal5State.UNKNOWN
        self.check()

    @property
    def meta_dir(self):
        return self.directory / ".seal5"

    @property
    def deps_dir(self):
        return self.meta_dir / "deps"

    @property
    def build_dir(self):
        return self.meta_dir / "build"

    @property
    def install_dir(self):
        return self.meta_dir / "install"

    @property
    def logs_dir(self):
        return self.meta_dir / "logs"

    @property
    def models_dir(self):
        return self.meta_dir / "models"

    @property
    def temp_dir(self):
        return self.meta_dir / "temp"

    def check(self):
        pass

    def initialize(
        self,
        interactive: bool = False,
        clone: bool = False,
        clone_url: Optional[str] = None,
        clone_ref: Optional[str] = None,
        force: bool = False,
    ):
        logger.info("Initializing Seal5")
        if not self.directory.is_dir():
            if clone is False and not ask_user("Clone LLVM repository?", default=False, interactive=interactive):
                logging.error(f"Target directory does not exist! Aborting...")
                sys.exit(1)
            clone_llvm_repo(self.directory, clone_url, ref=clone_ref)
        if self.meta_dir.is_dir():
            if force is False and not ask_user("Overwrite existing .seal5 diretcory?", default=False, interactive=interactive):
                logging.error(f"Directory {self.meta_dir} already exists! Aborting...")
                sys.exit(1)
        self.meta_dir.mkdir(exist_ok=True)
        create_seal5_directories(self.meta_dir, ["deps", "models", "logs", "build", "install", "temp"])
        logger.info("Completed initialization of Seal5")

    def setup(
        self,
        interactive: bool = False,
        force: bool = False,
    ):
        logger.info("Installing Seal5 dependencies")
        m2isar_dependency.clone(self.deps_dir / "M2-ISA-R", overwrite=force)
        # cdsl2llvm_dependency.clone(self.deps_dir / "cdsl2llvm", overwrite=force)
        logger.info("Completed installation of Seal5 dependencies")

    def load_cfg(self, file: Path):
        pass  # TODO

    def load_cdsl(self, file: Path):
        pass  # TODO

    def load(self, files: List[Path]):
        logger.info("Loading Seal5 inputs")
        for file in files:
            logger.info("Processing file: %s", file)
            ext = file.suffix
            if ext.lower() in [".yml", ".yaml"]:
                self.load_cfg(file)
            elif ext.lower() in [".core_desc"]:
                self.load_cdsl(file)
            else:
                raise RuntimeError(f"Unsupported input type: {ext}")
        logger.info("Compledted load of Seal5 inputs")

    def build(self, options: dict = {}, debug: bool = False):
        logger.info("Building Seal5 LLVM")
        if options:
            raise NotImplementedError
        name = "debug" if debug else "release"
        build_llvm(self.directory, self.build_dir / name, debug=debug)
        logger.info("Completed build of Seal5 LLVM")

    def transform(self):
        logger.info("Tranforming Seal5 models")
        raise NotImplementedError
        logger.info("Completed tranformation of Seal5 models")

    def generate(self):
        logger.info("Generating Seal5 patches")
        raise NotImplementedError
        logger.info("Completed generation of Seal5 patches")

    def apply(self):
        logger.info("Applying Seal5 patches")
        raise NotImplementedError
        logger.info("Completed application of Seal5 patches")

    def test(self):
        logger.info("Testing Seal5 LLVM")
        raise NotImplementedError
        logger.info("Completed test of Seal5 LLVM")

    def deploy(self):
        logger.info("Deploying Seal5 LLVM")
        raise NotImplementedError
        logger.info("Completed deployment of Seal5 LLVM")

    def export(self):
        logger.info("Exporting Seal5 artifacts")
        raise NotImplementedError
        logger.info("Completed export of Seal5 artifacts")

    def clean(self):
        logger.info("Cleaning Seal5 directories")
        raise NotImplementedError
        logger.info("Completed clean of Seal5 directories")

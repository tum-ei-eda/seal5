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
import os
import sys
import tarfile
from pathlib import Path
from typing import Optional, List, Dict, Tuple

import git

from seal5.logging import get_logger, set_log_file, set_log_level
from seal5.types import Seal5State, PatchStage
from seal5.settings import Seal5Settings, PatchSettings, DEFAULT_SETTINGS, LLVMConfig

from seal5.dependencies import cdsl2llvm_dependency
from seal5 import utils
from seal5.tools import llvm, cdsl2llvm, inject_patches
from seal5.resources.resources import get_patches
from seal5.index import File, NamedPatch, write_index_yaml

logger = get_logger()


def lookup_manual_patch(patch: PatchSettings, allow_missing=False):
    patches = get_patches(patch_name=patch.name, target=patch.target, allow_empty=allow_missing)
    if len(patches) == 0:
        # fallback (undefined target)
        patches = get_patches(patch_name=patch.name, target=None, allow_empty=allow_missing)
    if len(patches) == 0:
        raise RuntimeError(f"Manual patch '{patch.name}' not found!")
    assert len(patches) == 1, "Too many matches"
    res = patches[0]
    if patch.target is None:
        target = res.parent.name
        patch.target = str(target)
    if patch.file is None:
        patch.file = str(res)
    return res


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


class Seal5Flow:
    def __init__(self, directory: Optional[Path] = None, name: str = "default"):
        self.directory: Path = handle_directory(directory)
        self.name: str = name
        self.state: Seal5State = Seal5State.UNKNOWN
        self.check()
        self.settings: Seal5Settings = None
        if self.settings_file.is_file():
            self.settings = Seal5Settings.from_yaml_file(self.settings_file)
        if self.logs_dir.is_dir():
            pass
            set_log_file(self.log_file_path)
            if self.settings:
                set_log_level(
                    console_level=self.settings.logging.console.level, file_level=self.settings.logging.file.level
                )

    @property
    def meta_dir(self):
        return self.directory / ".seal5"

    @property
    def settings_file(self):
        return self.meta_dir / "settings.yml"

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
    def inputs_dir(self):
        return self.meta_dir / "inputs"

    @property
    def temp_dir(self):
        return self.meta_dir / "temp"

    @property
    def gen_dir(self):
        return self.meta_dir / "gen"

    @property
    def patches_dir(self):  # TODO: maybe merge with gen_dir
        return self.meta_dir / "patches"

    @property
    def log_file_path(self):
        return self.logs_dir / "seal5.log"

    def check(self):
        pass

    def initialize(
        self,
        interactive: bool = False,
        clone: bool = False,
        clone_url: Optional[str] = None,
        clone_ref: Optional[str] = None,
        force: bool = False,
        verbose: bool = False,
    ):
        logger.info("Initializing Seal5")
        sha = None
        if not self.directory.is_dir():
            if clone is False and not utils.ask_user("Clone LLVM repository?", default=False, interactive=interactive):
                logger.error("Target directory does not exist! Aborting...")
                sys.exit(1)
            sha = llvm.clone_llvm_repo(self.directory, clone_url, ref=clone_ref, label=self.name)
        else:
            if force:
                sha = llvm.clone_llvm_repo(self.directory, clone_url, ref=clone_ref, refresh=True, label=self.name)
        if self.meta_dir.is_dir():
            if force is False and not utils.ask_user(
                "Overwrite existing .seal5 diretcory?", default=False, interactive=interactive
            ):
                logger.error(f"Directory {self.meta_dir} already exists! Aborting...")
                sys.exit(1)
        self.meta_dir.mkdir(exist_ok=True)
        create_seal5_directories(
            self.meta_dir, ["deps", "models", "logs", "build", "install", "temp", "inputs", "gen", "patches"]
        )
        self.settings = Seal5Settings.from_dict(DEFAULT_SETTINGS)
        if sha:
            self.settings.llvm.state.base_commit = sha
        self.settings.to_yaml_file(self.settings_file)
        set_log_file(self.log_file_path)
        set_log_level(console_level=self.settings.logging.console.level, file_level=self.settings.logging.file.level)
        logger.info("Completed initialization of Seal5")

    def setup(
        self,
        interactive: bool = False,
        force: bool = False,
        verbose: bool = False,
    ):
        logger.info("Installing Seal5 dependencies")
        # m2isar_dependency.clone(self.deps_dir / "M2-ISA-R", overwrite=force)
        logger.info("Cloning CDSL2LLVM")
        # cdsl2llvm_dependency.clone(self.deps_dir / "cdsl2llvm", overwrite=force, depth=1)
        cdsl2llvm_dependency.clone(self.deps_dir / "cdsl2llvm", overwrite=force)
        logger.info("Building PatternGen")
        llvm_config = LLVMConfig(
            options={
                "CMAKE_BUILD_TYPE": "Release",
                "LLVM_BUILD_TOOLS": False,
                "LLVM_ENABLE_ASSERTIONS": False,
                "LLVM_OPTIMIZED_TABLEGEN": True,
                "LLVM_ENABLE_PROJECT": [],
                "LLVM_TARGETS_TO_BUILD": ["RISCV"],
            }
        )
        # llvm_config = LLVMConfig(options={"CMAKE_BUILD_TYPE": "Debug", "LLVM_BUILD_TOOLS": False, "LLVM_ENABLE_ASSERTIONS": False, "LLVM_OPTIMIZED_TABLEGEN": True, "LLVM_ENABLE_PROJECT": [], "LLVM_TARGETS_TO_BUILD": ["RISCV"]})
        cmake_options = llvm_config.options
        cdsl2llvm.build_pattern_gen(
            self.deps_dir / "cdsl2llvm",
            self.deps_dir / "cdsl2llvm" / "llvm" / "build",
            cmake_options=cmake_options,
            use_ninja=True,
        )
        logger.info("Completed build of PatternGen")
        logger.info("Building llc")
        cdsl2llvm.build_llc(
            self.deps_dir / "cdsl2llvm",
            self.deps_dir / "cdsl2llvm" / "llvm" / "build",
            cmake_options=cmake_options,
            use_ninja=True,
        )
        logger.info("Completed build of llc")
        # input("qqqqqq")
        logger.info("Completed installation of Seal5 dependencies")

    def load_cfg(self, file: Path, overwrite: bool = False):
        new_settings: Seal5Settings = Seal5Settings.from_yaml_file(file)
        self.settings.merge(new_settings, overwrite=overwrite)
        self.settings.to_yaml_file(self.settings_file)

    def prepare_environment(self):
        env = os.environ.copy()
        # env["PYTHONPATH"] = str(self.deps_dir / "M2-ISA-R")
        env["CDSL2LLVM_DIR"] = str(self.deps_dir / "cdsl2llvm")
        return env

    def parse_coredsl(self, file, out_dir, verbose: bool = False):
        args = [
            file,
            "-o",
            out_dir,
        ]
        utils.python(
            "-m",
            "seal5.frontends.coredsl2_seal5.parser",
            *args,
            env=self.prepare_environment(),
            print_func=logger.info if verbose else logger.debug,
            live=True,
        )

    def load_cdsl(self, file: Path, verbose: bool = False, overwrite: bool = False):
        assert file.is_file(), "TODO"
        filename: str = file.name
        dest = self.inputs_dir / filename
        if dest.is_file() and not overwrite:
            raise RuntimeError(f"File {filename} already loaded!")
        # Add file to inputs directory and settings
        utils.copy(file, dest)
        self.settings.inputs.append(filename)
        # Parse CoreDSL file with M2-ISA-R (TODO: Standalone)
        dest = self.models_dir
        self.parse_coredsl(file, dest, verbose=verbose)
        self.settings.to_yaml_file(self.settings_file)

    def load(self, files: List[Path], verbose: bool = False, overwrite: bool = False):
        logger.info("Loading Seal5 inputs")
        for file in files:
            logger.info("Processing file: %s", file)
            ext = file.suffix
            if ext.lower() in [".yml", ".yaml"]:
                self.load_cfg(file, overwrite=overwrite)
            elif ext.lower() in [".core_desc"]:
                self.load_cdsl(file, verbose=verbose, overwrite=overwrite)
            else:
                raise RuntimeError(f"Unsupported input type: {ext}")
        # TODO: only allow single instr set for now and track inputs in settings
        logger.info("Completed load of Seal5 inputs")

    def build(self, config="release", verbose: bool = False):
        logger.info("Building Seal5 LLVM")
        llvm_config = self.settings.llvm.configs.get(config, None)
        assert llvm_config is not None, f"Invalid llvm config: {config}"
        cmake_options = llvm_config.options
        llvm.build_llvm(self.directory, self.build_dir / config, cmake_options)
        logger.info("Completed build of Seal5 LLVM")

    def convert_models(self, verbose: bool = False, inplace: bool = False):
        assert not inplace
        input_files = list(self.models_dir.glob("*.m2isarmodel"))
        assert len(input_files) > 0, "No input models found!"
        for input_file in input_files:
            name = input_file.name
            base = input_file.stem
            new_name = f"{base}.seal5model"
            logger.info("Converting %s -> %s", name, new_name)
            args = [
                self.models_dir / name,
                "-o",
                self.models_dir / new_name,
                "--log",
                "info",
                # "debug",
            ]
            utils.python(
                "-m",
                "seal5.transform.converter",
                *args,
                env=self.prepare_environment(),
                print_func=logger.info if verbose else logger.debug,
                live=True,
            )

    def optimize_model(self, verbose: bool = False, inplace: bool = True):
        assert inplace
        input_files = list(self.models_dir.glob("*.seal5model"))
        assert len(input_files) > 0, "No Seal5 models found!"
        for input_file in input_files:
            name = input_file.name
            logger.info("Optimizing %s", name)
            args = [
                self.models_dir / name,
                "--log",
                "info",
                # "debug",
            ]
            utils.python(
                "-m",
                "seal5.transform.optimize_instructions.optimizer",
                *args,
                env=self.prepare_environment(),
                print_func=logger.info if verbose else logger.debug,
                live=True,
            )

    def infer_types(self, verbose: bool = False, inplace: bool = True):
        assert inplace
        input_files = list(self.models_dir.glob("*.seal5model"))
        assert len(input_files) > 0, "No Seal5 models found!"
        for input_file in input_files:
            name = input_file.name
            logger.info("Infering types for %s", name)
            args = [
                self.models_dir / name,
                "--log",
                "info",
                # "debug",
            ]
            utils.python(
                "-m",
                "seal5.transform.infer_types.transform",
                *args,
                env=self.prepare_environment(),
                print_func=logger.info if verbose else logger.debug,
                live=True,
            )

    def simplify_trivial_slices(self, verbose: bool = False, inplace: bool = True):
        assert inplace
        input_files = list(self.models_dir.glob("*.seal5model"))
        assert len(input_files) > 0, "No Seal5 models found!"
        for input_file in input_files:
            name = input_file.name
            logger.info("Simplifying trivial slices for %s", name)
            args = [
                self.models_dir / name,
                "--log",
                "info",
                # "debug",
            ]
            utils.python(
                "-m",
                "seal5.transform.simplify_trivial_slices.transform",
                *args,
                env=self.prepare_environment(),
                print_func=logger.info if verbose else logger.debug,
                live=True,
            )

    def explicit_truncations(self, verbose: bool = False, inplace: bool = True):
        assert inplace
        input_files = list(self.models_dir.glob("*.seal5model"))
        assert len(input_files) > 0, "No Seal5 models found!"
        for input_file in input_files:
            name = input_file.name
            logger.info("Adding excplicit truncations for %s", name)
            args = [
                self.models_dir / name,
                "--log",
                "info",
                # "debug",
            ]
            utils.python(
                "-m",
                "seal5.transform.explicit_truncations.transform",
                *args,
                env=self.prepare_environment(),
                print_func=logger.info if verbose else logger.debug,
                live=True,
            )

    def process_settings(self, verbose: bool = False, inplace: bool = True):
        assert inplace
        input_files = list(self.models_dir.glob("*.seal5model"))
        assert len(input_files) > 0, "No Seal5 models found!"
        for input_file in input_files:
            name = input_file.name
            logger.info("Processing settings for %s", name)
            args = [
                self.models_dir / name,
                "--log",
                "info",
                # "debug",
                "--yaml",
                self.settings_file,
            ]
            utils.python(
                "-m",
                "seal5.transform.process_settings.transform",
                *args,
                env=self.prepare_environment(),
                print_func=logger.info if verbose else logger.debug,
                live=True,
            )

    def filter_model(self, verbose: bool = False, inplace: bool = True):
        assert inplace
        input_files = list(self.models_dir.glob("*.seal5model"))
        assert len(input_files) > 0, "No Seal5 models found!"
        for input_file in input_files:
            name = input_file.name
            logger.info("Filtering %s", name)
            filter_settings = self.settings.filter
            filter_args = []

            def get_filter_args(settings, suffix):
                ret = []
                keep = list(map(str, settings.keep))
                drop = list(map(str, settings.drop))
                if keep:
                    ret += [f"--keep-{suffix}", ",".join(keep)]
                if drop:
                    ret += [f"--drop-{suffix}", ",".join(drop)]
                return ret

            filter_sets = filter_settings.sets
            filter_instructions = filter_settings.instructions
            filter_aliases = filter_settings.aliases
            filter_intrinsics = filter_settings.intrinsics
            filter_opcodes = filter_settings.opcodes
            filter_encoding_sizes = filter_settings.encoding_sizes
            # TODO: filter_functions
            filter_args.extend(get_filter_args(filter_sets, "sets"))
            filter_args.extend(get_filter_args(filter_instructions, "instructions"))
            filter_args.extend(get_filter_args(filter_aliases, "aliases"))
            filter_args.extend(get_filter_args(filter_intrinsics, "intrinsics"))
            filter_args.extend(get_filter_args(filter_opcodes, "opcodes"))
            filter_args.extend(get_filter_args(filter_encoding_sizes, "encoding-sizes"))
            args = [
                self.models_dir / name,
                *filter_args,
                "--log",
                # "info",
                "debug",
            ]
            utils.python(
                "-m",
                "seal5.transform.filter_model.filter",
                *args,
                env=self.prepare_environment(),
                print_func=logger.info if verbose else logger.debug,
                live=True,
            )

    def drop_unused(self, verbose: bool = False, inplace: bool = True):
        assert inplace
        input_files = list(self.models_dir.glob("*.seal5model"))
        assert len(input_files) > 0, "No Seal5 models found!"
        for input_file in input_files:
            name = input_file.name
            logger.info("Dropping unused for %s", name)
            args = [
                self.models_dir / name,
                "--log",
                # "info",
                "debug",
            ]
            utils.python(
                "-m",
                "seal5.transform.drop_unused.optimizer",
                *args,
                env=self.prepare_environment(),
                print_func=logger.info if verbose else logger.debug,
                live=True,
            )

    def detect_registers(self, verbose: bool = False, inplace: bool = True):
        assert inplace
        input_files = list(self.models_dir.glob("*.seal5model"))
        assert len(input_files) > 0, "No Seal5 models found!"
        for input_file in input_files:
            name = input_file.name
            logger.info("Detecting registers for %s", name)
            args = [
                self.models_dir / name,
                "--log",
                "info",
                # "debug",
            ]
            utils.python(
                "-m",
                "seal5.transform.detect_registers",
                *args,
                env=self.prepare_environment(),
                print_func=logger.info if verbose else logger.debug,
                live=True,
            )

    def detect_behavior_constraints(self, verbose: bool = False, inplace: bool = True):
        assert inplace
        input_files = list(self.models_dir.glob("*.seal5model"))
        assert len(input_files) > 0, "No Seal5 models found!"
        for input_file in input_files:
            name = input_file.name
            logger.info("Collecting constraints for %s", name)
            args = [
                self.models_dir / name,
                "--log",
                # "info",
                "debug",
            ]
            utils.python(
                "-m",
                "seal5.transform.collect_raises.collect",
                *args,
                env=self.prepare_environment(),
                print_func=logger.info if verbose else logger.debug,
                live=True,
            )

    def detect_side_effects(self, verbose: bool = False, inplace: bool = True):
        assert inplace
        input_files = list(self.models_dir.glob("*.seal5model"))
        assert len(input_files) > 0, "No Seal5 models found!"
        for input_file in input_files:
            name = input_file.name
            logger.info("Detecting side effects for %s", name)
            args = [
                self.models_dir / name,
                "--log",
                # "info",
                "debug",
            ]
            utils.python(
                "-m",
                "seal5.transform.detect_side_effects.collect",
                *args,
                env=self.prepare_environment(),
                print_func=logger.info if verbose else logger.debug,
                live=True,
            )

    def detect_inouts(self, verbose: bool = False, inplace: bool = True):
        assert inplace
        input_files = list(self.models_dir.glob("*.seal5model"))
        assert len(input_files) > 0, "No Seal5 models found!"
        for input_file in input_files:
            name = input_file.name
            logger.info("Detecting inouts for %s", name)
            args = [
                self.models_dir / name,
                "--log",
                # "info",
                "debug",
            ]
            utils.python(
                "-m",
                "seal5.transform.detect_inouts.collect",
                *args,
                env=self.prepare_environment(),
                print_func=logger.info if verbose else logger.debug,
                live=True,
            )

    def collect_operand_types(self, verbose: bool = False, inplace: bool = True):
        assert inplace
        input_files = list(self.models_dir.glob("*.seal5model"))
        assert len(input_files) > 0, "No Seal5 models found!"
        for input_file in input_files:
            # print("input_file", input_file)
            # input(">")
            name = input_file.name
            logger.info("Collecting operand types for %s", name)
            args = [
                self.models_dir / name,
                "--log",
                # "info",
                "debug",
                "--skip-failing",
            ]
            utils.python(
                "-m",
                "seal5.transform.collect_operand_types.collect",
                *args,
                env=self.prepare_environment(),
                print_func=logger.info if verbose else logger.debug,
                live=True,
            )
            # input("<")

    def collect_register_operands(self, verbose: bool = False, inplace: bool = True):
        assert inplace
        input_files = list(self.models_dir.glob("*.seal5model"))
        assert len(input_files) > 0, "No Seal5 models found!"
        for input_file in input_files:
            name = input_file.name
            logger.info("Collecting register operands for %s", name)
            args = [
                self.models_dir / name,
                "--log",
                # "info",
                "debug",
            ]
            utils.python(
                "-m",
                "seal5.transform.collect_register_operands.collect",
                *args,
                env=self.prepare_environment(),
                print_func=logger.info if verbose else logger.debug,
                live=True,
            )

    def collect_immediate_operands(self, verbose: bool = False, inplace: bool = True):
        assert inplace
        input_files = list(self.models_dir.glob("*.seal5model"))
        assert len(input_files) > 0, "No Seal5 models found!"
        for input_file in input_files:
            name = input_file.name
            logger.info("Collecting immediate operands for %s", name)
            args = [
                self.models_dir / name,
                "--log",
                # "info",
                "debug",
            ]
            utils.python(
                "-m",
                "seal5.transform.collect_immediate_operands.collect",
                *args,
                env=self.prepare_environment(),
                print_func=logger.info if verbose else logger.debug,
                live=True,
            )

    def eliminate_rd_cmp_zero(self, verbose: bool = False, inplace: bool = True):
        assert inplace
        input_files = list(self.models_dir.glob("*.seal5model"))
        assert len(input_files) > 0, "No Seal5 models found!"
        for input_file in input_files:
            name = input_file.name
            logger.info("Eliminating rd == 0 for %s", name)
            args = [
                self.models_dir / name,
                "--log",
                # "info",
                "debug",
            ]
            utils.python(
                "-m",
                "seal5.transform.eliminate_rd_cmp_zero.transform",
                *args,
                env=self.prepare_environment(),
                print_func=logger.info if verbose else logger.debug,
                live=True,
            )

    def eliminate_mod_rfs(self, verbose: bool = False, inplace: bool = True):
        assert inplace
        input_files = list(self.models_dir.glob("*.seal5model"))
        assert len(input_files) > 0, "No Seal5 models found!"
        for input_file in input_files:
            name = input_file.name
            logger.info("Eliminating op MOD RFS for %s", name)
            args = [
                self.models_dir / name,
                "--log",
                # "info",
                "debug",
            ]
            utils.python(
                "-m",
                "seal5.transform.eliminate_mod_rfs.transform",
                *args,
                env=self.prepare_environment(),
                print_func=logger.info if verbose else logger.debug,
                live=True,
            )

    def write_yaml(self, verbose: bool = False, inplace: bool = True):
        assert inplace
        input_files = list(self.models_dir.glob("*.seal5model"))
        assert len(input_files) > 0, "No Seal5 models found!"
        for input_file in input_files:
            name = input_file.name
            new_name = name.replace(".seal5model", ".yml")
            logger.info("Writing YAML for %s", name)
            args = [
                self.models_dir / name,
                "--log",
                # "info",
                "debug",
                "--output",
                self.temp_dir / new_name,
            ]
            utils.python(
                "-m",
                "seal5.backends.yaml.writer",
                *args,
                env=self.prepare_environment(),
                print_func=logger.info if verbose else logger.debug,
                live=True,
            )
            print(self.temp_dir / new_name)
            self.load_cfg(self.temp_dir / new_name, overwrite=False)

    def write_cdsl(self, verbose: bool = False, inplace: bool = True, split: bool = False, compat: bool = False):
        assert inplace
        input_files = list(self.models_dir.glob("*.seal5model"))
        assert len(input_files) > 0, "No Seal5 models found!"
        for input_file in input_files:
            name = input_file.name
            if split:
                new_name = name.replace(".seal5model", "")
            else:
                new_name = name.replace(".seal5model", ".core_desc")
            logger.info("Writing CDSL for %s", name)
            args = [
                self.models_dir / name,
                "--log",
                # "info",
                "debug",
                "--output",
                self.temp_dir / new_name,
            ]
            if split:
                (self.temp_dir / new_name).mkdir(exist_ok=True)
                args.append("--splitted")
            if compat:
                args.append("--compat")
            utils.python(
                "-m",
                "seal5.backends.coredsl2.writer",
                *args,
                env=self.prepare_environment(),
                print_func=logger.info if verbose else logger.debug,
                live=True,
            )
            # args_compat = [
            #     self.models_dir / name,
            #     "--log",
            #     # "info",
            #     "debug",
            #     "--output",
            #     self.temp_dir / f"{new_name}_compat",
            #     "--compat",
            # ]
            # if split:
            #     args.append("--splitted")
            # utils.python(
            #     "-m",
            #     "seal5.backends.coredsl2.writer",
            #     *args_compat,
            #     env=self.prepare_environment(),
            #     print_func=logger.info if verbose else logger.debug,
            #     live=True,
            # )

    # def write_cdsl_splitted(self, verbose: bool = False, inplace: bool = True):
    #     assert inplace
    #     # input_files = list(self.models_dir.glob("*.seal5model"))
    #     # assert len(input_files) > 0, "No Seal5 models found!"
    #     # for input_file in input_files:
    #     #     name = input_file.name
    #     #     sub = name.replace(".seal5model", "")
    #     for _ in [None]:
    #         set_names = list(self.settings.extensions.keys())
    #         # print("set_names", set_names)
    #         assert len(set_names) > 0, "No sets found"
    #         for set_name in set_names:
    #             insn_names = self.settings.extensions[set_name].instructions
    #             if insn_names is None:
    #                 logger.warning("Skipping empty set %s", set_name)
    #                 continue
    #             sub = self.settings.extensions[set_name].model
    #             # TODO: populate model in yaml backend!
    #             if sub is None:  # Fallback
    #                 sub = set_name
    #             input_file = self.models_dir / f"{sub}.seal5model"
    #             assert input_file.is_file(), f"File not found: {input_file}"
    #             assert len(insn_names) > 0, f"No instructions found in set: {set_name}"
    #             # insn_names = self.collect_instr_names()
    #             (self.temp_dir / sub / set_name).mkdir(exist_ok=True, parents=True)
    #             for insn_name in insn_names:
    #                 logger.info("Writing Metamodel for %s/%s/%s", sub, set_name, insn_name)
    #                 args = [
    #                     input_file,
    #                     "--keep-instructions",
    #                     insn_name,
    #                     "--log",
    #                     "debug",
    #                     # "info",
    #                     "--output",
    #                     self.temp_dir / sub / set_name / f"{insn_name}.seal5model",
    #                 ]
    #                 utils.python(
    #                     "-m",
    #                     "seal5.transform.filter_model.filter",
    #                     *args,
    #                     env=self.prepare_environment(),
    #                     print_func=logger.info if verbose else logger.debug,
    #                     live=True,
    #                 )
    #                 logger.info("Writing CDSL for %s/%s", sub, insn_name)
    #                 args = [
    #                     self.temp_dir / sub / set_name / f"{insn_name}.seal5model",
    #                     "--log",
    #                     "debug",
    #                     # "info",
    #                     "--output",
    #                     self.temp_dir / sub / set_name / f"{insn_name}.core_desc"
    #                 ]
    #                 utils.python(
    #                     "-m",
    #                     "seal5.backends.coredsl2.writer",
    #                     *args,
    #                     env=self.prepare_environment(),
    #                     print_func=logger.info if verbose else logger.debug,
    #                     live=True,
    #                 )
    #                 args_compat = [
    #                     self.temp_dir / sub / set_name / f"{insn_name}.seal5model",
    #                     "--log",
    #                     # "info",
    #                     "debug",
    #                     "--output",
    #                     self.temp_dir / sub / set_name / f"{insn_name}.core_desc_compat",
    #                     "--compat",
    #                 ]
    #                 utils.python(
    #                     "-m",
    #                     "seal5.backends.coredsl2.writer",
    #                     *args_compat,
    #                     env=self.prepare_environment(),
    #                     print_func=logger.info if verbose else logger.debug,
    #                     live=True,
    #                 )

    def convert_behav_to_llvmir(self, verbose: bool = False, inplace: bool = True):
        assert inplace
        # input_files = list(self.temp_dir.glob("*.core_desc_compat"))
        # TODO: use different file ext for non-compat?
        input_files = list(self.temp_dir.glob("*.core_desc"))
        assert len(input_files) > 0, "No files found!"
        errs = []
        for input_file in input_files:
            name = input_file.name
            # new_name = name.replace(".core_desc_compat", ".ll")
            # new_name = name.replace(".core_desc_compat", ".td")
            logger.info("Writing LLVM-IR for %s", name)
            try:
                cdsl2llvm.run_pattern_gen(
                    self.deps_dir / "cdsl2llvm" / "llvm" / "build",
                    input_file,
                    None,
                    skip_patterns=True,
                    skip_formats=True,
                )
            except AssertionError:
                pass
                # errs.append((str(input_file), str(ex)))
        if len(errs) > 0:
            print("errs", errs)

    def convert_behav_to_llvmir_splitted(self, verbose: bool = False, split: bool = True):
        assert split, "TODO"
        input_files = list(self.models_dir.glob("*.seal5model"))
        assert len(input_files) > 0, "No Seal5 models found!"
        gen_metrics_file = True
        for input_file in input_files:
            name = input_file.name
            if split:
                new_name = name.replace(".seal5model", "")
            else:
                new_name = name.replace(".seal5model", ".ll")
            logger.info("Writing LLVM-IR for %s", name)
            args = [
                self.models_dir / name,
                "--log",
                # "info",
                "debug",
                "--output",
                self.temp_dir / new_name,
            ]
            if split:
                (self.temp_dir / new_name).mkdir(exist_ok=True)
                args.append("--splitted")
            if gen_metrics_file:
                # TODO: move to .seal5/metrics
                metrics_file = self.temp_dir / (new_name + "_llvmir_metrics.csv")
                args.extend(["--metrics", metrics_file])
            utils.python(
                "-m",
                "seal5.backends.llvmir.writer",
                *args,
                env=self.prepare_environment(),
                print_func=logger.info if verbose else logger.debug,
                live=True,
            )

    def convert_behav_to_tablegen(self, verbose: bool = False, split: bool = True):
        assert split, "TODO"
        input_files = list(self.models_dir.glob("*.seal5model"))
        assert len(input_files) > 0, "No Seal5 models found!"
        formats = True
        gen_metrics_file = True
        gen_index_file = True
        for input_file in input_files:
            name = input_file.name
            if split:
                new_name = name.replace(".seal5model", "")
            else:
                new_name = name.replace(".seal5model", ".td")
            logger.info("Writing TableGen patterns for %s", name)
            args = [
                self.models_dir / name,
                "--log",
                # "info",
                "debug",
                "--output",
                self.temp_dir / new_name,
            ]
            if split:
                (self.temp_dir / new_name).mkdir(exist_ok=True)
                args.append("--splitted")
            if formats:
                args.append("--formats")
            if gen_metrics_file:
                metrics_file = self.temp_dir / (new_name + "_tblgen_patterns_metrics.csv")
                args.extend(["--metrics", metrics_file])
            if gen_index_file:
                index_file = self.temp_dir / (new_name + "_tblgen_patterns_index.yml")
                args.extend(["--index", index_file])
            utils.python(
                "-m",
                "seal5.backends.patterngen.writer",
                *args,
                env=self.prepare_environment(),
                print_func=logger.info if verbose else logger.debug,
                live=True,
            )
            if gen_index_file:
                if index_file.is_file():
                    patch_name = f"tblgen_patterns_{input_file.stem}"
                    patch_settings = PatchSettings(
                        name=patch_name,
                        stage=int(PatchStage.PHASE_2),
                        comment=f"CDSL2LLVM Generated Tablegen Patterns for {input_file.name}",
                        index=str(index_file),
                        generated=True,
                        target="llvm",
                    )
                    self.settings.patches.append(patch_settings)
                    self.settings.to_yaml_file(self.settings_file)
                else:
                    logger.warning("No patches found!")

    # def convert_behav_to_tablegen_splitted(self, verbose: bool = False, inplace: bool = True):
    #     assert inplace
    #     # input_files = list(self.models_dir.glob("*.seal5model"))
    #     # assert len(input_files) > 0, "No Seal5 models found!"
    #     errs = []
    #     # for input_file in input_files:
    #     #     name = input_file.name
    #     #     sub = name.replace(".seal5model", "")
    #     for _ in [None]:
    #         set_names = list(self.settings.extensions.keys())
    #         assert len(set_names) > 0, "No sets found"
    #         for set_name in set_names:
    #             insn_names = self.settings.extensions[set_name].instructions
    #             if insn_names is None:
    #                 logger.warning("Skipping empty set %s", set_name)
    #                 continue
    #             assert len(insn_names) > 0, f"No instructions found in set: {set_name}"
    #             sub = self.settings.extensions[set_name].model
    #             # TODO: populate model in yaml backend!
    #             if sub is None:  # Fallbacke
    #                 sub = set_name
    #             for insn_name in insn_names:
    #                 ll_file = self.temp_dir / sub / set_name / f"{insn_name}.ll"
    #                 if not ll_file.is_file():
    #                     logger.warning("Skipping %s due to errors.", insn_name)
    #                     continue
    #                 # input_file = self.temp_dir / sub / set_name / f"{insn_name}.core_desc_compat"
    #                 input_file = self.temp_dir / sub / set_name / f"{insn_name}.core_desc"
    #                 assert input_file.is_file(), f"File not found: {input_file}"
    #                 output_file = input_file.parent / (input_file.stem + ".td")
    #                 name = input_file.name
    #                 logger.info("Writing TableGen for %s", name)
    #                 ext = self.settings.extensions[set_name].feature
    #                 if ext is None:  # fallback to set_name
    #                     ext = set_name.replace("_", "")
    #                 try:
    #                     cdsl2llvm.run_pattern_gen(self.deps_dir / "cdsl2llvm" / "llvm" / "build", input_file, output_file, skip_patterns=False, skip_formats=False, ext=ext)
    #                 except AssertionError:
    #                     pass
    #                     # errs.append((insn_name, str(ex)))
    #     if len(errs) > 0:
    #         # print("errs", errs)
    #         for insn_name, err_str in errs:
    #             print("Err:", insn_name, err_str)
    #             input("!")

    def convert_llvmir_to_gmir_splitted(self, verbose: bool = False, inplace: bool = True):
        assert inplace
        # input_files = list(self.models_dir.glob("*.seal5model"))
        # assert len(input_files) > 0, "No Seal5 models found!"
        errs = []
        # for input_file in input_files:
        #     name = input_file.name
        #     sub = name.replace(".seal5model", "")
        for _ in [None]:
            set_names = list(self.settings.extensions.keys())
            assert len(set_names) > 0, "No sets found"
            for set_name in set_names:
                insn_names = self.settings.extensions[set_name].instructions
                if insn_names is None:
                    logger.warning("Skipping empty set %s", set_name)
                    continue
                assert len(insn_names) > 0, f"No instructions found in set: {set_name}"
                sub = self.settings.extensions[set_name].model
                # TODO: populate model in yaml backend!
                if sub is None:  # Fallbacke
                    sub = set_name
                for insn_name in insn_names:
                    ll_file = self.temp_dir / sub / set_name / f"{insn_name}.ll"
                    if not ll_file.is_file():
                        logger.warning("Skipping %s due to errors.", insn_name)
                        continue
                    output_file = ll_file.parent / (ll_file.stem + ".gmir")
                    name = ll_file.name
                    logger.info("Writing gmir for %s", name)
                    try:
                        cdsl2llvm.convert_ll_to_gmir(
                            self.deps_dir / "cdsl2llvm" / "llvm" / "build", ll_file, output_file
                        )
                    except AssertionError:
                        pass
                        # errs.append((insn_name, str(ex)))
        if len(errs) > 0:
            # print("errs", errs)
            for insn_name, err_str in errs:
                print("Err:", insn_name, err_str)
                input("!")

    def gen_seal5_td(self, verbose: bool = False):
        patch_name = "seal5_td"
        dest = "llvm/lib/Target/RISCV/seal5.td"
        dest2 = "llvm/lib/Target/RISCV/RISCV.td"
        content = """
// Includes
// seal5.td - seal5_td_includes - INSERTION_START
// seal5.td - seal5_td_includes - INSERTION_END
"""
        content2 = """
include "seal5.td"
"""
        file_artifact = File(
            dest,
            content=content,
        )
        patch_artifact = NamedPatch(
            dest2,
            key="riscv_td_includes",
            content=content2,
        )
        artifacts = [file_artifact, patch_artifact]

        index_file = self.temp_dir / "seal5_td_index.yml"
        write_index_yaml(index_file, artifacts, {}, content=True)
        patch_settings = PatchSettings(
            name=patch_name,
            stage=int(PatchStage.PHASE_1),
            comment="Add seal5.td to llvm/lib/Target/RISCV",
            index=str(index_file),
            generated=True,
            target="llvm",
        )
        self.settings.patches.append(patch_settings)

    def transform(self, verbose: bool = False):
        logger.info("Tranforming Seal5 models")
        inplace = True
        if not inplace:
            raise NotImplementedError()
        # TODO: flow.models: Seal5ModelWrapper -> transform(verbose: bool = False, *kwargs)
        # first convert M2-ISA-R MetaModel to Seal5 Metamodel
        self.convert_models(verbose=verbose)
        # filter model
        self.filter_model(verbose=verbose)
        # add aliases to model
        # self.add_aliases(verbose=verbose)
        # add intrinsics
        # self.add_intrinsics(verbose=verbose)
        # drop unused constants
        self.drop_unused(verbose=verbose)
        self.eliminate_rd_cmp_zero(verbose=verbose)
        self.eliminate_mod_rfs(verbose=verbose)
        self.drop_unused(verbose=verbose)
        # optimize Seal5 Metamodel
        self.optimize_model(verbose=verbose)
        self.infer_types(verbose=verbose)
        self.simplify_trivial_slices(verbose=verbose)
        self.explicit_truncations(verbose=verbose)
        self.process_settings(verbose=verbose)
        self.write_yaml(verbose=verbose)
        # determine dyn constraints (eliminate raise)
        self.detect_behavior_constraints(verbose=verbose)
        # determine operand types
        self.collect_register_operands(verbose=verbose)
        self.collect_immediate_operands(verbose=verbose)
        self.collect_operand_types(verbose=verbose)
        # detect side effects
        self.detect_side_effects(verbose=verbose)
        # detect ins/outs
        self.detect_inouts(verbose=verbose)
        # detect registers
        self.detect_registers(verbose=verbose)
        # TODO: determine static constraints (xlen,...) -> subtargetvmap
        # detect memory adressing modes
        # self.detect_adressing_modes(verbose)  # TODO
        # detect legal GMIR ops (and map to selectiondag?)
        # self.detect_legal_ops(verbose=verbose)  # TODO
        # extract costs/heuristics
        # self.extract_costs_and_heuristics(verbose)  # TODO

        logger.info("Completed tranformation of Seal5 models")

    def generate(self, verbose: bool = False):
        logger.info("Generating Seal5 patches")
        # raise NotImplementedError
        patches = []
        skip = []  # TODO: User, Global, PerInstr
        # TODO: only: []

        # Prerequisites
        self.write_cdsl(verbose=verbose, split=True, compat=True)
        self.gen_seal5_td(verbose=verbose)

        # # General
        # if "subtarget_features" not in skip:
        #     patches.extend(self.gen_subtarget_feature_patches())
        # if "subtarget_tests" not in skip:
        #     patches.extend(self.gen_subtarget_tests_patches())

        # # MC Level
        # if "register_types" not in skip:
        #     patches.extend(self.gen_register_types_patches())
        # if "operand_types" not in skip:
        #     patches.extend(self.gen_operand_types_patches())
        # if "instruction_formats" not in skip:
        #     patches.extend(self.gen_instruction_format_patches())
        # if "instruction_infos" not in skip:
        #     patches.extend(self.gen_instruction_infos_patches())
        # if "disassembler" not in skip:
        #     patches.extend(self.gen_disassembler_patches())
        # if "mc_tests" not in skip:
        #     patches.extend(self.gen_mc_tests_patches())

        # # Codegen Level
        # if "selection_dag_legalizer" not in skip:
        #     patches.extend(self.gen_selection_dag_legalizer_patches())
        # if "globalisel_legalizer" not in skip:
        #     patches.extend(self.gen_globalisel_legalizer_patches())
        # if "scalar_costs" not in skip:
        #     patches.extend(self.gen_scalar_costs_patches())
        # if "simd_costs" not in skip:
        #     patches.extend(self.gen_simd_costs_patches())
        # if "isel_patterns" not in skip:
        #     patches.extend(self.gen_isel_patterns_patches())
        # if "codegen_test" not in skip:
        #     patches.extend(self.gen_codegen_tests_patches())

        # Others
        if "pattern_gen" not in skip:
            self.convert_behav_to_llvmir_splitted(verbose=verbose)  # TODO: add split arg
            self.convert_llvmir_to_gmir_splitted(verbose=verbose)  # TODO: add split arg
            self.convert_behav_to_tablegen(verbose=verbose, split=True)

        logger.info("Completed generation of Seal5 patches")

    # def collect_patches(self, stage: Optional[PatchStage]):
    #     return ret

    def collect_patches(self):
        # generated patches
        temp: Dict[Tuple[str, str], PatchSettings] = {}

        # user-defined patches
        patches_settings = self.settings.patches
        for patch_settings in patches_settings:
            if patch_settings.stage is None:
                patch_settings.stage = int(PatchStage.PHASE_0)
                logger.warning("Undefined patch stage for patch %s. Defaulting to PHASE_0", patch_settings.name)
                # raise NotImplementedError("Undefined patch stage!")
            if patch_settings.generated:  # not manual
                if patch_settings.target != "llvm":
                    raise NotImplementedError("Only supporting llvm patches so far")
                if patch_settings.file is None:
                    assert patch_settings.index
                    name = patch_settings.name
                    target = patch_settings.target
                    key = (target, name)
                    dest = self.patches_dir / target
                    patch_settings.to_yaml_file(dest / f"{name}.yml")
                    # assert key not in temp
                    if key in temp:
                        # override
                        logger.debug("Overriding existing patch settings")
                        new = temp[key]
                        new.merge(patch_settings)
                        temp[key] = new
                    else:
                        temp[key] = patch_settings
                else:
                    raise NotImplementedError("Only supporting index based patches so far")
            else:
                patch_file = lookup_manual_patch(patch_settings, allow_missing=True)
                # print("patch_file", patch_file)
                target = patch_settings.target
                name = patch_settings.name
                key = (target, name)
                if key in temp:
                    # override
                    logger.debug("Overriding existing patch settings")
                    new = temp[key]
                    new.merge(patch_settings)
                    temp[key] = new
                else:
                    temp[key] = patch_settings
                if patch_file:
                    logger.debug("Copying custom patch_file %s", patch_file)
                    dest = self.patches_dir / target
                    dest.mkdir(exist_ok=True)
                    # print("dest", dest)
                    utils.copy(patch_file, dest / f"{name}.patch")
                    patch_settings.to_yaml_file(dest / f"{name}.yml")
        ret = {}
        for patch_settings in temp.values():
            if patch_settings.stage not in ret:
                ret[patch_settings.stage] = []
            ret[patch_settings.stage].append(patch_settings)
        # print("ret", ret)
        # input("!r!")
        return ret

    def resolve_patch_file(self, path):
        assert path is not None, "Patch path undefined"
        if isinstance(path, str):
            path = Path(path)
        assert isinstance(path, Path)
        ret = path
        if ret.is_file():
            return path.resolve()
        ret = self.patches_dir / path
        if ret.is_file():
            return ret.resolve()
        raise RuntimeError(f"Patch file {path} not found!")

    def apply_patch(self, patch: PatchSettings, force: bool = False):
        name = patch.name
        target = patch.target
        if patch.enable:
            logger.info("Applying patch '%s' on '%s'", name, target)
        else:
            logger.info("Skipping patch '%s' on '%s'", name, target)
            return
        if patch.index:
            # use inject_extensions_script
            file = self.patches_dir / target / f"{name}.patch"
            # assert not file.is_file(), f"Patch already exists: {file}"
            prefix = self.settings.git.prefix
            comment = patch.comment
            msg = f"{prefix} {comment}"
            llvm_dir = self.directory
            inject_patches.generate_patch(
                patch.index,
                llvm_dir=llvm_dir,
                out_file=file,
                author=self.settings.git.author,
                mail=self.settings.git.mail,
                msg=msg,
                append=True,
            )

        else:
            file = self.resolve_patch_file(patch.file)
        dest = None
        if target == "llvm":
            dest = self.directory
            repo = git.Repo(dest)
            if not llvm.check_llvm_repo(dest):
                if force:
                    repo.git.reset(".")
                    repo.git.restore(".")
                else:
                    raise RuntimeError("LLVM repository is not clean!")
        if dest is None:
            raise RuntimeError(f"Unsupported patch target: {target}")
        # TODO: check if clean
        repo.git.apply(file)
        author = self.settings.git.author
        mail = self.settings.git.mail
        actor = git.Actor(author, mail)
        prefix = self.settings.git.prefix
        msg = patch.comment
        if not msg:
            msg = f"Apply patch: {patch.name}"
        if prefix:
            msg = prefix + " " + msg
        repo.git.add(A=True)
        repo.index.commit(msg, author=actor)
        patch.applied = True
        self.settings.to_yaml_file(self.settings_file)
        # TODO: commit

    def patch(self, verbose: bool = False, stages: List[PatchStage] = None, force: bool = False):
        logger.info("Applying Seal5 patches")
        if stages is None:
            stages = list(map(PatchStage, range(PatchStage.PHASE_4)))
        assert len(stages) > 0
        patches_per_stage = self.collect_patches()
        for stage in stages:
            logger.info("Current stage: %s", stage)
            patches = patches_per_stage.get(stage, [])
            # print("patches", patches)
            for patch in patches:
                if patch.applied:
                    # skipping
                    continue
                self.apply_patch(patch, force=force)
        logger.info("Completed application of Seal5 patches")

    def test(self, debug: bool = False, verbose: bool = False, ignore_error: bool = False):
        logger.info("Testing Seal5 LLVM")
        name = "debug" if debug else "release"
        test_paths = self.settings.test.paths
        failing_tests = llvm.test_llvm(
            self.directory / "llvm" / "test", self.build_dir / name, test_paths, verbose=verbose
        )
        if len(failing_tests) > 0:
            logger.error("%d tests failed: %s", len(failing_tests), ", ".join(failing_tests))
            if not ignore_error:
                raise RuntimeError("Tests failed!")
        logger.info("Completed test of Seal5 LLVM")

    def deploy(self, verbose: bool = False):
        logger.info("Deploying Seal5 LLVM")
        logger.info("Completed deployment of Seal5 LLVM")

    def export(self, dest: Path, verbose: bool = False):
        logger.info("Exporting Seal5 artifacts")
        if isinstance(dest, str):
            dest = Path(dest)
        suffix = dest.suffix
        if suffix != ".gz":
            raise NotImplementedError("Only .tar.gz export is supported!")
        artifacts = [self.inputs_dir, self.gen_dir, self.models_dir, self.logs_dir, self.settings_file]
        with tarfile.open(dest, mode="w:gz") as archive:
            for artifact in artifacts:
                name = str(artifact)
                assert str(self.meta_dir) in name
                name = name.replace(f"{self.meta_dir}/", "")
                if artifact.is_file():
                    archive.add(artifact, arcname=name)
                elif artifact.is_dir():
                    archive.add(artifact, arcname=name, recursive=True)

        logger.info("Completed export of Seal5 artifacts")

    def reset(self, settings: bool = True, verbose: bool = False, interactive: bool = False):
        logger.info("Cleaning Seal5 state")
        if interactive:
            raise NotImplementedError
        if settings:
            self.settings.reset()
        logger.info("Completed clean of Seal5 settings")

    def clean(self, verbose: bool = False, interactive: bool = False):
        logger.info("Cleaning Seal5 directories")
        to_clean = [
            self.temp_dir,
            self.gen_dir,
            self.models_dir,
            self.inputs_dir,
            self.logs_dir,
            self.install_dir,
            self.build_dir,
            self.deps_dir,
        ]
        for path in to_clean:
            utils.clean_path(path, interactive=interactive)
        # self.reset(verbose=verbose, interactive=interactive)
        logger.info("Completed clean of Seal5 directories")

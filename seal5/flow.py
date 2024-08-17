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
import time
import glob
import tarfile
from pathlib import Path
from typing import Optional, List, Dict, Tuple, Union

import git

from seal5.logging import get_logger, set_log_file, set_log_level
from seal5.types import Seal5State, PatchStage
from seal5.settings import Seal5Settings, PatchSettings, DEFAULT_SETTINGS, LLVMConfig, LLVMVersion

from seal5.dependencies import CDSL2LLVMDependency
from seal5 import utils
from seal5.tools import llvm, cdsl2llvm, inject_patches
from seal5.resources.resources import get_patches, get_test_cfg
from seal5.passes import Seal5Pass, PassType, PassScope, PassManager, filter_passes
import seal5.pass_list as passes

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
        directory = Path(directory)
    return directory.resolve()


def handle_meta_dir(meta_dir: Optional[Union[str, Path]], directory: Union[str, Path], name: str):
    # TODO: handle environment vars
    if meta_dir is None:
        meta_dir = "default"
    if meta_dir == "default":
        if not isinstance(directory, Path):
            assert isinstance(directory, str)
            directory = Path(directory)
        meta_dir = directory / ".seal5"
    elif meta_dir == "user":
        # config_dir = get_seal5_user_config_dir()
        raise NotImplementedError("store meta dirs in .config/seal5/meta")
    if not isinstance(meta_dir, Path):
        assert isinstance(meta_dir, str)
        meta_dir = Path(meta_dir)
    return meta_dir.resolve()


def create_seal5_directories(path: Path, directories: list):
    logger.debug("Creating Seal5 directories")
    if not isinstance(path, Path):
        path = Path(path)
    if not path.is_dir():
        raise RuntimeError(f"Not a diretory: {path}")
    for directory in directories:
        (path / directory).mkdir(parents=True, exist_ok=True)


def add_test_cfg(tests_dir: Path):
    dest = tests_dir / "lit.cfg.py"
    logger.debug("Creating test cfg %s", dest)
    src = get_test_cfg()
    utils.copy(src, dest)


class Seal5Flow:
    def __init__(
        self, directory: Optional[Path] = None, meta_dir: Optional[Union[str, Path]] = None, name: Optional[str] = None
    ):
        self.directory: Path = handle_directory(directory)
        self.meta_dir: Path = handle_meta_dir(meta_dir, directory, name)
        self.name: str = name
        self.state: Seal5State = Seal5State.UNKNOWN
        self.passes: List[Seal5Pass] = []
        self.repo: Optional[git.Repo] = git.Repo(self.directory) if self.directory.is_dir() else None
        self.check()
        self.settings = Seal5Settings.from_dict({"meta_dir": str(self.meta_dir), **DEFAULT_SETTINGS})
        # self.settings: Seal5Settings = Seal5Settings(directory=self.directory)
        self.settings.directory = str(self.directory)
        if self.settings.settings_file.is_file():
            self.settings = Seal5Settings.from_yaml_file(self.settings.settings_file)
            self.meta_dir = self.settings._meta_dir
        if self.settings.logs_dir.is_dir():
            set_log_file(self.settings.log_file_path)
            if self.settings:
                set_log_level(
                    console_level=self.settings.logging.console.level, file_level=self.settings.logging.file.level
                )
        self.name = self.settings.name if name is None else name
        self.settings.name = self.name
        self.settings.name = self.settings.name if name is None else name
        self.reset_passes()
        self.create_passes()
        # self.init_global_model()

    # def init_global_model(self, name: str = "Seal5"):
    #     dest = self.inputs_dir / f"{name}.seal5model"
    #     args = [
    #         "-",
    #         "-o",
    #         dest,
    #     ]
    #     utils.python(
    #         "-m",
    #         "seal5.frontends.dummy.writer",
    #         *args,
    #         env=env,
    #         print_func=logger.info if verbose else logger.debug,
    #         live=True,
    #     )

    #     self.update_global_model(name=name)

    # def update_global_model(self, name: str = "Seal5"):
    #     self.process_settings(name)

    def reset_passes(self):
        self.passes = []

    def add_pass(self, pass_: Seal5Pass):
        pass_names = [p.name for p in self.passes]
        assert pass_.name not in pass_names, f"Duplicate pass name: {pass_.name}"
        self.passes.append(pass_)

    def add_passes(self, pass_list: List[Seal5Pass]):
        for pass_ in pass_list:
            self.add_pass(pass_)

    def create_passes(self):
        # Transforms
        TRANSFORM_PASS_MAP = [
            # TODO: Global -> Model
            ("convert_models", passes.convert_models, {}),
            ("filter_models", passes.filter_model, {}),
            ("drop_unused", passes.drop_unused, {}),
            ("eliminate_rd_cmp_zero", passes.eliminate_rd_cmp_zero, {}),
            ("eliminate_mod_rfs", passes.eliminate_mod_rfs, {}),
            ("drop_unused2", passes.drop_unused, {}),
            ("optimize_model", passes.optimize_model, {}),
            ("infer_types", passes.infer_types, {}),
            ("simplify_trivial_slices", passes.simplify_trivial_slices, {}),
            ("explicit_truncations", passes.explicit_truncations, {}),
            ("process_settings", passes.process_settings, {}),
            ("write_yaml", passes.write_yaml, {}),
            ("detect_behavior_constraints", passes.detect_behavior_constraints, {}),
            ("collect_register_operands", passes.collect_register_operands, {}),
            ("collect_immediate_operands", passes.collect_immediate_operands, {}),
            ("collect_operand_types", passes.collect_operand_types, {}),
            ("detect_side_effects", passes.detect_side_effects, {}),
            ("detect_inouts", passes.detect_inouts, {}),
            ("detect_registers", passes.detect_registers, {}),
            ("write_cdsl_full", passes.write_cdsl, {"split": False, "compat": False}),
            # TODO: determine static constraints (xlen,...) -> subtargetvmap
            # detect memory adressing modes
            # self.detect_adressing_modes(verbose)  # TODO
            # detect legal GMIR ops (and map to selectiondag?)
            # self.detect_legal_ops(verbose=verbose)  # TODO
            # extract costs/heuristics
            # self.extract_costs_and_heuristics(verbose)  # TODO
            # ("split_models", passes.split_models, {"by_set": False, "by_instr": False}),
        ]
        for pass_name, pass_handler, pass_options in TRANSFORM_PASS_MAP:
            pass_scope = PassScope.MODEL
            self.add_pass(Seal5Pass(pass_name, PassType.TRANSFORM, pass_scope, pass_handler, options=pass_options))

        # Generates
        GENERATE_PASS_MAP = [
            ("seal5_td", passes.gen_seal5_td, {}),
            # ("model_td", passes.gen_model_td, {}),
            ("set_td", passes.gen_set_td, {}),
            ("riscv_features", passes.gen_riscv_features_patch, {}),
            ("riscv_isa_infos", passes.gen_riscv_isa_info_patch, {}),
            # ("riscv_instr_formats", passes.gen_riscv_instr_formats_patch, {}),
            ("riscv_instr_info", passes.gen_riscv_instr_info_patch, {}),
            # subtarget_tests
            # register_types
            # operand_types
            # instruction_formats
            # instruction_infos
            # disassembler
            # mc_tests
            # selection_dag_legalizer
            # scalar_costs
            # simd_costs
            # isel_patterns
            # codegen_test
            ("riscv_gisel_legalizer", passes.gen_riscv_gisel_legalizer_patch, {}),
            # TODO: nested pass lists?
            ("pattern_gen", passes.pattern_gen_pass, {}),
        ]
        for pass_name, pass_handler, pass_options in GENERATE_PASS_MAP:
            if pass_name in ["seal5_td", "riscv_gisel_legalizer"]:
                pass_scope = PassScope.GLOBAL
            else:
                pass_scope = PassScope.MODEL
            self.add_pass(Seal5Pass(pass_name, PassType.GENERATE, pass_scope, pass_handler, options=pass_options))

    def check(self):
        pass

    def initialize(
        self,
        interactive: bool = False,
        clone: bool = False,
        clone_url: Optional[str] = None,
        clone_ref: Optional[str] = None,
        clone_depth: Optional[int] = None,
        progress: bool = False,
        force: bool = False,
        verbose: bool = False,
    ):
        logger.info("Initializing Seal5")
        start = time.time()
        metrics = {}
        sha = None
        version_info = None
        if not self.directory.is_dir():
            if clone is False and not utils.ask_user("Clone LLVM repository?", default=False, interactive=interactive):
                logger.error("Target directory does not exist! Aborting...")
                sys.exit(1)
            logger.info("Cloning LLVM Repository")
            self.repo, sha, version_info = llvm.clone_llvm_repo(
                self.directory,
                clone_url,
                ref=clone_ref,
                label=self.name,
                git_settings=self.settings.git,
                depth=int(clone_depth) if clone_depth is not None else self.settings.llvm.clone_depth,
                progress=progress,
            )
        else:
            if force:
                logger.info("Updating LLVM Repository")
                self.repo, sha, version_info = llvm.clone_llvm_repo(
                    self.directory,
                    clone_url,
                    ref=clone_ref,
                    refresh=True,
                    label=self.name,
                    git_settings=self.settings.git,
                    depth=clone_depth or self.settings.llvm.clone_depth,
                )
        if self.meta_dir.is_dir():
            if force is False and not utils.ask_user(
                "Overwrite existing .seal5 diretcory?", default=False, interactive=interactive
            ):
                logger.error(f"Directory {self.meta_dir} already exists! Aborting...")
                sys.exit(1)
        self.meta_dir.mkdir(exist_ok=True)
        create_seal5_directories(
            self.meta_dir,
            ["deps", "models", "logs", "build", "install", "temp", "inputs", "gen", "patches", "tests"],
        )
        add_test_cfg(self.settings.tests_dir)
        if version_info:
            llvm_version = LLVMVersion(**version_info)
            self.settings.llvm.state.version = llvm_version
        if sha:
            self.settings.llvm.state.base_commit = sha
        self.settings.save()
        set_log_file(self.settings.log_file_path)
        set_log_level(console_level=self.settings.logging.console.level, file_level=self.settings.logging.file.level)
        end = time.time()
        diff = end - start
        metrics["time_s"] = diff
        self.settings.metrics.append({"initialize": metrics})
        self.settings.save()
        logger.info("Completed initialization of Seal5")

    def setup(
        self,
        interactive: bool = False,
        force: bool = False,
        progress: bool = False,
        verbose: bool = False,
    ):
        logger.info("Installing Seal5 dependencies")
        start = time.time()
        metrics = {}
        logger.info("Cloning CDSL2LLVM")
        # cdsl2llvm_dependency.clone(self.settings.deps_dir / "cdsl2llvm", overwrite=force, depth=1)
        pattern_gen_settings = self.settings.tools.pattern_gen
        kwargs = {}
        if pattern_gen_settings.clone_url is not None:
            kwargs["clone_url"] = pattern_gen_settings.clone_url
        if pattern_gen_settings.ref is not None:
            kwargs["ref"] = pattern_gen_settings.ref
        cdsl2llvm_dependency = CDSL2LLVMDependency(**kwargs)
        cdsl2llvm_dependency.clone(
            self.settings.deps_dir / "cdsl2llvm",
            overwrite=force,
            depth=pattern_gen_settings.clone_depth,
            sparse=pattern_gen_settings.sparse_checkout,
            progress=progress,
        )
        integrated_pattern_gen = self.settings.tools.pattern_gen.integrated
        if integrated_pattern_gen:
            logger.info("Adding PatternGen to target LLVM")
            patch_settings = cdsl2llvm.get_pattern_gen_patches(
                self.settings.deps_dir / "cdsl2llvm",
                self.settings.temp_dir,
            )
            self.settings.add_patch(patch_settings)
        else:
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
            cmake_options = llvm_config.options
            cdsl2llvm.build_pattern_gen(
                self.settings.deps_dir / "cdsl2llvm",
                self.settings.deps_dir / "cdsl2llvm" / "llvm" / "build",
                cmake_options=cmake_options,
                use_ninja=self.settings.llvm.ninja,
            )
            logger.info("Completed build of PatternGen")
            logger.info("Building llc")
            cdsl2llvm.build_llc(
                self.settings.deps_dir / "cdsl2llvm",
                self.settings.deps_dir / "cdsl2llvm" / "llvm" / "build",
                cmake_options=cmake_options,
                use_ninja=self.settings.llvm.ninja,
            )
            logger.info("Completed build of llc")
        # input("qqqqqq")
        end = time.time()
        diff = end - start
        metrics["time_s"] = diff
        self.settings.metrics.append({"setup": metrics})
        self.settings.save()
        logger.info("Completed installation of Seal5 dependencies")

    def load_cfg(self, file: Path, overwrite: bool = False):
        assert file.is_file(), f"File does not exist: {file}"
        new_settings: Seal5Settings = Seal5Settings.from_yaml_file(file)
        self.settings.merge(new_settings, overwrite=overwrite)
        self.settings.save()

    def load_test(self, file: Path, overwrite: bool = True):
        assert file.is_file(), f"File does not exist: {file}"
        filename: str = file.name
        dest = self.settings.tests_dir / filename
        if dest.is_file() and not overwrite:
            raise RuntimeError(f"File {filename} already loaded!")
        utils.copy(file, dest)
        if str(dest) not in self.settings.test.paths:
            self.settings.test.paths.append(str(dest))
            self.settings.save()

    def prepare_environment(self):
        env = os.environ.copy()
        # env["PYTHONPATH"] = str(self.settings.deps_dir / "M2-ISA-R")
        cdsl2llvm_build_dir = None
        integrated_pattern_gen = self.settings.tools.pattern_gen.integrated
        if integrated_pattern_gen:
            default_config_name = self.settings.llvm.default_config
            non_default_config_names = [
                config_name for config_name in self.settings.llvm.configs.keys() if config_name != default_config_name
            ]
            config_names = [default_config_name, *non_default_config_names]
            for config_name in config_names:
                cdsl2llvm_build_dir = self.settings.build_dir / config_name
                if cdsl2llvm_build_dir.is_dir():
                    break
        else:
            cdsl2llvm_build_dir = self.settings.deps_dir / "cdsl2llvm" / "llvm" / "build"
        if cdsl2llvm_build_dir.is_dir():
            cdsl2llvm_build_dir = str(cdsl2llvm_build_dir)
            env["CDSL2LLVM_DIR"] = cdsl2llvm_build_dir
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
        assert file.is_file(), f"File does not exist: {file}"
        filename: str = file.name
        dest = self.settings.inputs_dir / filename
        if dest.is_file() and not overwrite:
            raise RuntimeError(f"File {filename} already loaded!")
        # Add file to inputs directory and settings
        utils.copy(file, dest)
        self.settings.inputs.append(filename)
        # Parse CoreDSL file with M2-ISA-R (TODO: Standalone)
        dest = self.settings.models_dir
        self.parse_coredsl(file, dest, verbose=verbose)
        self.settings.save()

    def load(self, files: List[Path], verbose: bool = False, overwrite: bool = False):
        logger.info("Loading Seal5 inputs")
        # Expand glob patterns

        def glob_helper(file):
            res = glob.glob(str(file))
            assert len(res) > 0, f"No files found for pattern: {file}"
            return list(map(Path, res))

        files = sum([glob_helper(file) for file in files], [])
        for file in files:
            logger.info("Processing file: %s", file)
            ext = file.suffix
            if ext.lower() in [".yml", ".yaml"]:
                self.load_cfg(file, overwrite=overwrite)
            elif ext.lower() in [".core_desc"]:
                self.load_cdsl(file, verbose=verbose, overwrite=overwrite)
            elif ext.lower() in [".ll", ".c", ".cc", ".cpp", ".s", ".mir", ".gmir"]:
                self.load_test(file, overwrite=overwrite)
            else:
                raise RuntimeError(f"Unsupported input type: {ext}")
        # TODO: only allow single instr set for now and track inputs in settings
        logger.info("Completed load of Seal5 inputs")

    def build(self, config=None, target="all", verbose: bool = False):
        logger.info("Building Seal5 LLVM (%s)", target)
        start = time.time()
        metrics = {}
        if config is None:
            config = self.settings.llvm.default_config
        llvm_config = self.settings.llvm.configs.get(config, None)
        assert llvm_config is not None, f"Invalid llvm config: {config}"
        cmake_options = llvm_config.options
        llvm.build_llvm(
            Path(self.settings.directory),
            self.settings.build_dir / config,
            cmake_options=cmake_options,
            target=target,
            use_ninja=self.settings.llvm.ninja,
        )
        end = time.time()
        diff = end - start
        metrics["time_s"] = diff
        self.settings.metrics.append({"build": metrics})
        self.settings.save()
        logger.info("Completed build of Seal5 LLVM (%s)", target)

    def install(self, dest: Optional[Union[str, Path]] = None, config=None, verbose: bool = False):
        # TODO: implement compress?
        if dest is None:
            dest = self.settings.install_dir / config
        if not isinstance(dest, Path):
            dest = Path(dest)
        dest.mkdir(exist_ok=True)
        logger.info("Installing Seal5 LLVM to: %s", dest)
        start = time.time()
        metrics = {}
        if config is None:
            config = self.settings.llvm.default_config
        llvm_config = self.settings.llvm.configs.get(config, None)
        assert llvm_config is not None, f"Invalid llvm config: {config}"
        cmake_options = llvm_config.options
        llvm.build_llvm(
            Path(self.settings.directory),
            self.settings.build_dir / config,
            cmake_options=cmake_options,
            use_ninja=self.settings.llvm.ninja,
            target=None,
            install=True,
            install_dir=dest,
        )
        end = time.time()
        diff = end - start
        metrics["time_s"] = diff
        self.settings.metrics.append({"build": metrics})
        self.settings.save()
        logger.info("Completed install of Seal5 LLVM")

    def transform(self, verbose: bool = False, skip: Optional[List[str]] = None, only: Optional[List[str]] = None):
        logger.info("Tranforming Seal5 models")
        start = time.time()
        metrics = {"passes": []}
        passes_settings = self.settings.passes
        assert passes_settings is not None
        assert passes_settings.defaults is not None
        default_skip = passes_settings.defaults.skip
        if skip is None and default_skip:
            skip = default_skip
        default_only = passes_settings.defaults.only
        if only is None and default_only:
            only = default_only
        # inplace = True
        # if not inplace:
        #     raise NotImplementedError()

        input_models = self.settings.model_names
        transform_passes = filter_passes(self.passes, pass_type=PassType.TRANSFORM)
        with PassManager("transform_passes", transform_passes, skip=skip, only=only) as pm:
            result = pm.run(input_models, settings=self.settings, env=self.prepare_environment(), verbose=verbose)
            if result:
                metrics_ = result.metrics
                if metrics_:
                    metrics["passes"].append({pm.name: metrics_})

        end = time.time()
        diff = end - start
        metrics["time_s"] = diff
        self.settings.metrics.append({"transform": metrics})
        self.settings.save()
        logger.info("Completed tranformation of Seal5 models")

    def generate(self, verbose: bool = False, skip: Optional[List[str]] = None, only: Optional[List[str]] = None):
        logger.info("Generating Seal5 patches")
        start = time.time()
        metrics = {"passes": []}
        generate_passes = filter_passes(self.passes, pass_type=PassType.GENERATE)
        # TODO: User, Global, PerInstr
        input_models = self.settings.model_names
        with PassManager("generate_passes", generate_passes, skip=skip, only=only) as pm:
            result = pm.run(input_models, settings=self.settings, env=self.prepare_environment(), verbose=verbose)
            if result:
                metrics_ = result.metrics
                if metrics_:
                    metrics["passes"].append({pm.name: metrics_})

        end = time.time()
        diff = end - start
        metrics["time_s"] = diff
        self.settings.metrics.append({"generate": metrics})
        self.settings.save()
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
                    dest = self.settings.patches_dir / target
                    dest.mkdir(exist_ok=True)
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
                    dest = self.settings.patches_dir / target
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
        ret = self.settings.patches_dir / path
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
            file = self.settings.patches_dir / target / f"{name}.patch"
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
        self.settings.save()
        # TODO: commit

    def patch(self, verbose: bool = False, stages: List[PatchStage] = None, force: bool = False):
        logger.info("Applying Seal5 patches")
        start = time.time()
        metrics = {}
        if stages is None:
            stages = list(map(PatchStage, range(PatchStage.PHASE_5 + 1)))
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
            assert self.repo is not None
            tag_name = f"seal5-{self.name}-stage{int(stage)}"
            tag_msg = f"Patched Seal5 LLVM after stage {stage}"
            # author = git_.get_author(self.settings.git)
            # self.repo.create_tag(tag_name, message=tag_msg, force=True, author=author)
            self.repo.create_tag(tag_name, message=tag_msg, force=True)
        end = time.time()
        diff = end - start
        metrics["time_s"] = diff
        self.settings.metrics.append({"patch": metrics})
        self.settings.save()
        logger.info("Completed application of Seal5 patches")

    def test(
        self, debug: bool = False, verbose: bool = False, ignore_error: bool = False, config: Optional[str] = None
    ):
        logger.info("Testing Seal5 LLVM")
        start = time.time()
        metrics = {}
        if config is None:
            config = self.settings.llvm.default_config
        test_paths = self.settings.test.paths
        failing_tests = llvm.test_llvm(
            self.directory / "llvm" / "test", self.settings.build_dir / config, test_paths, verbose=verbose
        )
        if len(failing_tests) > 0:
            logger.error("%d tests failed: %s", len(failing_tests), ", ".join(failing_tests))
            if not ignore_error:
                raise RuntimeError("Tests failed!")
        end = time.time()
        diff = end - start
        metrics["time_s"] = diff
        self.settings.metrics.append({"test": metrics})
        self.settings.save()
        logger.info("Completed test of Seal5 LLVM")

    def deploy(self, dest: Path, verbose: bool = False, stage: PatchStage = PatchStage.PHASE_5):
        assert dest is not None
        # Archive source files
        logger.info("Deploying Seal5 LLVM")
        start = time.time()
        metrics = {}
        # TODO: move to different file
        tag_name = f"seal5-{self.name}-stage{int(stage)}"
        self.repo.git.archive(tag_name, "-o", dest)
        end = time.time()
        diff = end - start
        metrics["time_s"] = diff
        self.settings.metrics.append({"deploy": metrics})
        self.settings.save()
        logger.info("Completed deployment of Seal5 LLVM")

    def export(self, dest: Path, verbose: bool = False):
        logger.info("Exporting Seal5 artifacts")
        start = time.time()
        metrics = {}
        assert dest is not None
        if isinstance(dest, str):
            dest = Path(dest)
        suffix = dest.suffix
        if suffix != ".gz":
            raise NotImplementedError("Only .tar.gz export is supported!")
        artifacts = [
            self.settings.inputs_dir,
            self.settings.gen_dir,
            self.settings.patches_dir,
            self.settings.inputs_dir,
            self.settings.tests_dir,
            self.settings.models_dir,
            self.settings.logs_dir,
            self.settings.settings_file,
        ]
        with tarfile.open(dest, mode="w:gz") as archive:
            for artifact in artifacts:
                name = str(artifact)
                assert str(self.meta_dir) in name
                name = name.replace(f"{self.meta_dir}/", "")
                if artifact.is_file():
                    archive.add(artifact, arcname=name)
                elif artifact.is_dir():
                    archive.add(artifact, arcname=name, recursive=True)

        end = time.time()
        diff = end - start
        metrics["time_s"] = diff
        self.settings.metrics.append({"export": metrics})
        self.settings.save()
        logger.info("Completed export of Seal5 artifacts")

    def reset(self, settings: bool = True, verbose: bool = False, interactive: bool = False):
        logger.info("Cleaning Seal5 state")
        start = time.time()
        metrics = {}
        if interactive:
            raise NotImplementedError
        if settings:
            self.settings.reset()
        end = time.time()
        diff = end - start
        metrics["time_s"] = diff
        self.settings.metrics.append({"reset": metrics})
        if self.meta_dir.is_dir():
            self.settings.save()
        logger.info("Completed clean of Seal5 settings")

    def clean(
        self,
        temp: bool = False,
        patches: bool = False,
        models: bool = False,
        inputs: bool = False,
        logs: bool = False,
        install: bool = False,
        build: bool = False,
        deps: bool = False,
        verbose: bool = False,
        interactive: bool = False,
    ):
        logger.info("Cleaning Seal5 directories")
        start = time.time()
        metrics = {}
        to_clean = []
        if temp:
            to_clean.append(self.settings.temp_dir)
        if patches:
            to_clean.append(self.settings.patches_dir)
        if models:
            to_clean.append(self.settings.models_dir)
        if inputs:
            to_clean.append(self.settings.inputs_dir)
        if logs:
            to_clean.append(self.settings.logs_dir)
        if install:
            to_clean.append(self.settings.install_dir)
        if build:
            to_clean.append(self.settings.build_dir)
        if deps:
            to_clean.append(self.settings.deps_dir)
        # if gen:
        #     to_clean.append(self.settings.gen_dir)
        for path in to_clean:
            utils.clean_path(path, interactive=interactive)
        # self.reset(verbose=verbose, interactive=interactive)
        end = time.time()
        diff = end - start
        metrics["time_s"] = diff
        self.settings.metrics.append({"clean": metrics})
        if self.meta_dir.is_dir():
            self.settings.save()
        logger.info("Completed clean of Seal5 directories")

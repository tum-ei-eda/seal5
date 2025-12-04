"""Wrappers for running the seal5 flow with minimal efforts."""

import os
from typing import Optional, Union, List

# import logging
from pathlib import Path

from seal5.logging import Logger

from seal5.flow import Seal5Flow
from seal5.types import PatchStage
from seal5.utils import str2bool
from seal5.logging import update_log_level


logger = Logger("wrapper")


def group_files(files: List[Union[str, Path]]):
    """Split the given files per extension."""
    files = list(map(Path, files))
    cdsl_files = []
    cfg_files = []
    test_files = []
    other_files = []
    for file in files:
        suffix = file.suffix.lower()
        if suffix in [".core_desc", ".cdsl"]:
            cdsl_files.append(file)
        elif suffix in [".yml", ".yaml"]:
            cfg_files.append(file)
        elif suffix in [".c", ".cc", ".cpp", ".ll", ".mir", ".s"]:
            test_files.append(file)
        else:
            other_files.append(file)
    return cdsl_files, cfg_files, test_files, other_files


def prepatched_helper(val):
    if isinstance(val, str) and val.lower() == "auto":
        return "auto"
    return str2bool(val)


# Parameters
OUT_DIR = os.environ.get("OUT_DIR", None)
INSTALL_DIR = os.environ.get("INSTALL_DIR", None)
VERBOSE = str2bool(os.environ.get("VERBOSE", 0))
SKIP_PATTERNS = str2bool(os.environ.get("SKIP_PATTERNS", 0))
INTERACTIVE = str2bool(os.environ.get("INTERACTIVE", 0))
PREPATCHED = prepatched_helper(os.environ.get("PREPATCHED", "auto"))  # Possible values: [0,1,auto]
LLVM_URL = os.environ.get("LLVM_URL", "https://github.com/llvm/llvm-project.git")
LLVM_REF = os.environ.get("LLVM_REF", "llvmorg-19.1.7")
BUILD_CONFIG = os.environ.get("BUILD_CONFIG", None)
IGNORE_ERROR = str2bool(os.environ.get("IGNORE_ERROR", 1))
IGNORE_LLVM_IMM_TYPES = str2bool(os.environ.get("IGNORE_LLVM_IMM_TYPES", 0))
LOAD = str2bool(os.environ.get("LOAD", 1))
TRANSFORM = str2bool(os.environ.get("TRANSFORM", 1))
GENERATE = str2bool(os.environ.get("GENERATE", 1))
PATCH = str2bool(os.environ.get("PATCH", 1))
BUILD = str2bool(os.environ.get("BUILD", 1))
TEST = str2bool(os.environ.get("TEST", 1))
INSTALL = str2bool(os.environ.get("INSTALL", 1))
DEPLOY = str2bool(os.environ.get("DEPLOY", 1))
EXPORT = str2bool(os.environ.get("EXPORT", 1))
CLEANUP = str2bool(os.environ.get("CLEANUP", 0))
RESET = str2bool(os.environ.get("RESET", 1))
INIT = str2bool(os.environ.get("INIT", 1))
SETUP = str2bool(os.environ.get("SETUP", 1))
PROGRESS = str2bool(os.environ.get("PROGRESS", 1))
CCACHE = str2bool(os.environ.get("CCACHE", 0))
BUILD_CACHE = str2bool(os.environ.get("BUILD_CACHE", 0))
CLONE_DEPTH = int(os.environ.get("CLONE_DEPTH", -1))
LOG_LEVEL = os.environ.get("SEAL5_LOG_LEVEL", None)
NAME = os.environ.get("NAME", None)


def run_seal5_flow(
    input_files: List[Union[str, Path]],
    dest: Optional[Union[str, Path]] = None,
    out_dir: Optional[Union[str, Path]] = OUT_DIR,
    install_dir: Optional[Union[str, Path]] = INSTALL_DIR,
    name: Optional[str] = NAME,
    interactive: bool = INTERACTIVE,
    prepatched: bool = PREPATCHED,
    llvm_url: str = LLVM_URL,
    llvm_ref: str = LLVM_REF,
    verbose: bool = VERBOSE,
    clone_depth: Optional[int] = CLONE_DEPTH,
    progress: bool = PROGRESS,
    build_config: Optional[str] = BUILD_CONFIG,
    ccache: bool = CCACHE,
    enable_build_cache: bool = BUILD_CACHE,
    ignore_error: bool = IGNORE_ERROR,
    skip_patterns: bool = SKIP_PATTERNS,
    load: bool = LOAD,
    transform: bool = TRANSFORM,
    generate: bool = GENERATE,
    patch: bool = PATCH,
    build: bool = BUILD,
    test: bool = TEST,
    install: bool = INSTALL,
    deploy: bool = DEPLOY,
    export: bool = EXPORT,
    cleanup: bool = CLEANUP,
    reset: bool = RESET,
    init: bool = INIT,
    setup: bool = SETUP,
    ignore_llvm_imm_types: bool = IGNORE_LLVM_IMM_TYPES,
    log_level: Optional[str] = LOG_LEVEL,
):
    """Single entry point (wrapper) to excute the full seal5 flow for a given set of files."""
    seal5_flow = Seal5Flow(dest, name=name)

    # Optional: clean existing settings/models for fresh run
    if reset:
        seal5_flow.reset(settings=True, interactive=interactive)
        seal5_flow.clean(temp=True, patches=True, models=True, inputs=True, interactive=interactive)

    has_stage0_tag = not (seal5_flow.repo is None or f"seal5-{seal5_flow.name}-stage0" not in seal5_flow.repo.tags)
    if prepatched == "auto":
        prepatched = has_stage0_tag
    if prepatched:
        assert has_stage0_tag, "PREPATCHED can only be used after LLVM was patched at least once."
        logger.info("Skipping PHASE0 patch using PREPATCHED feature.")

    # Clone LLVM and init seal5 metadata directory
    if init:
        seal5_flow.initialize(
            clone=True,
            clone_url=llvm_url,
            clone_ref=f"seal5-{seal5_flow.name}-stage0" if prepatched else llvm_ref,
            clone_depth=clone_depth,
            progress=progress,
            force=True,
            verbose=verbose,
            ignore_llvm_imm_types=ignore_llvm_imm_types,
        )

    # Override log_level
    if log_level is not None:
        # seal5_flow.logger.parent.handlers[0].setLevel(log_level.upper())
        update_log_level(log_level)

    if load:
        if len(input_files) == 0:
            logger.warning("No input files provided")
        cdsl_files, cfg_files, test_files, other_files = group_files(input_files)

        # Load CoreDSL inputs
        seal5_flow.load(cdsl_files, verbose=verbose, overwrite=True)

        # Load test inputs
        seal5_flow.load(test_files, verbose=verbose, overwrite=True)

        # Load YAML inputs
        seal5_flow.load(cfg_files, verbose=verbose, overwrite=False)

        # Load other inputs
        seal5_flow.load(other_files, verbose=verbose, overwrite=False)

    # Override settings from Python
    if build_config is not None:
        seal5_flow.settings.llvm.default_config = build_config

    # Clone & install Seal5 dependencies
    # 1. CDSL2LLVM (add PHASE_0 patches)
    if setup:
        seal5_flow.setup(force=True, progress=progress, verbose=verbose, skip_patterns=skip_patterns)

    # Apply initial patches
    if not prepatched:
        seal5_flow.patch(verbose=verbose, stages=[PatchStage.PHASE_0])

    if build:
        # Build initial LLVM
        seal5_flow.build(
            verbose=verbose, config=build_config, enable_ccache=ccache, enable_build_cache=enable_build_cache
        )

    if transform:
        # Transform inputs
        #   1. Create M2-ISA-R metamodel
        #   2. Convert to Seal5 metamodel (including aliases, builtins,...)
        #   3. Analyse/optimize instructions
        seal5_flow.transform(verbose=verbose)

    if generate:
        # Generate patches (except Patterns)
        seal5_flow.generate(verbose=verbose, skip=["pattern_gen"])

    if patch:
        # Apply next patches
        seal5_flow.patch(verbose=verbose, stages=[PatchStage.PHASE_1, PatchStage.PHASE_2])

    if build:
        # Build patched LLVM
        seal5_flow.build(
            verbose=verbose, config=build_config, enable_ccache=ccache, enable_build_cache=enable_build_cache
        )

    if not skip_patterns:
        if build:
            # Build PatternGen & llc
            seal5_flow.build(
                verbose=verbose,
                config=build_config,
                target="pattern-gen",
                enable_ccache=ccache,
                enable_build_cache=enable_build_cache,
            )
            seal5_flow.build(
                verbose=verbose,
                config=build_config,
                target="llc",
                enable_ccache=ccache,
                enable_build_cache=enable_build_cache,
            )

        if generate:
            # Generate remaining patches
            seal5_flow.generate(verbose=VERBOSE, only=["pattern_gen"])

        if patch:
            # Apply patches
            seal5_flow.patch(verbose=verbose, stages=list(range(PatchStage.PHASE_3, PatchStage.PHASE_5 + 1)))

    if build:
        # Build patched LLVM
        seal5_flow.build(
            verbose=verbose, config=build_config, enable_ccache=ccache, enable_build_cache=enable_build_cache
        )

    if test:
        # Test patched LLVM
        seal5_flow.test(verbose=verbose, ignore_error=ignore_error)

    if install:
        # Install final LLVM
        if install_dir is None and out_dir is not None:
            install_dir = Path(out_dir) / "seal5_llvm_install"
        seal5_flow.install(dest=install_dir, verbose=verbose, config=build_config, enable_ccache=ccache)

    if deploy:
        # Deploy patched LLVM (export sources)
        # TODO: combine commits and create tag
        seal5_flow.deploy(
            f"{dest}_source.zip" if out_dir is None else Path(out_dir) / "seal5_llvm_source.zip", verbose=verbose
        )

    if export:
        # Export patches, logs, reports
        seal5_flow.export(f"{dest}.tar.gz" if out_dir is None else Path(out_dir) / "seal5.tar.gz", verbose=verbose)

    if cleanup:
        # Optional: cleanup temorary files, build dirs,...
        seal5_flow.clean(temp=True, patches=True, models=True, inputs=True, interactive=interactive)

"""Wrappers for running the seal5 flow with minimal efforts."""

import os
from typing import Optional, Union, List

# import logging
from pathlib import Path

from seal5.flow import Seal5Flow
from seal5.types import PatchStage
from seal5.utils import str2bool
from seal5.logging import get_logger


logger = get_logger()


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


# Parameters
VERBOSE = str2bool(os.environ.get("VERBOSE", 0))
SKIP_PATTERNS = str2bool(os.environ.get("SKIP_PATTERNS", 0))
INTERACTIVE = str2bool(os.environ.get("INTERACTIVE", 0))
PREPATCHED = str2bool(os.environ.get("PREPATCHED", 0))
LLVM_URL = os.environ.get("LLVM_URL", "https://github.com/llvm/llvm-project.git")
LLVM_REF = os.environ.get("LLVM_REF", "llvmorg-19.1.7")
BUILD_CONFIG = os.environ.get("BUILD_CONFIG", None)
IGNORE_ERROR = str2bool(os.environ.get("IGNORE_ERROR", 1))
IGNORE_LLVM_IMM_TYPES = str2bool(os.environ.get("IGNORE_LLVM_IMM_TYPES", 0))
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
CLONE_DEPTH = int(os.environ.get("CLONE_DEPTH", -1))
NAME = os.environ.get("NAME", None)


def run_seal5_flow(
    input_files: List[Union[str, Path]],
    dest: Optional[Union[str, Path]] = None,
    out_dir: Optional[Union[str, Path]] = None,
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
    ignore_error: bool = IGNORE_ERROR,
    skip_patterns: bool = SKIP_PATTERNS,
    test: bool = TEST,
    install: bool = INSTALL,
    deploy: bool = DEPLOY,
    export: bool = EXPORT,
    cleanup: bool = CLEANUP,
    reset: bool = RESET,
    init: bool = INIT,
    setup: bool = SETUP,
    ignore_llvm_imm_types: bool = IGNORE_LLVM_IMM_TYPES,
):
    """Single entry point (wrapper) to excute the full seal5 flow for a given set of files."""
    seal5_flow = Seal5Flow(dest, name=name)

    # Optional: clean existing settings/models for fresh run
    if reset:
        seal5_flow.reset(settings=True, interactive=interactive)
        seal5_flow.clean(temp=True, patches=True, models=True, inputs=True, interactive=interactive)

    if prepatched:
        if seal5_flow.repo is None or f"seal5-{seal5_flow.name}-stage0" not in seal5_flow.repo.tags:
            raise RuntimeError("PREPATCHED can only be used after LLVM was patched at least once.")

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
        seal5_flow.setup(force=True, progress=progress, verbose=verbose)

    # Apply initial patches
    if not prepatched:
        seal5_flow.patch(verbose=verbose, stages=[PatchStage.PHASE_0])

    # Build initial LLVM
    seal5_flow.build(verbose=verbose, config=build_config, enable_ccache=ccache)

    # Transform inputs
    #   1. Create M2-ISA-R metamodel
    #   2. Convert to Seal5 metamodel (including aliases, builtins,...)
    #   3. Analyse/optimize instructions
    seal5_flow.transform(verbose=verbose)

    # Generate patches (except Patterns)
    seal5_flow.generate(verbose=verbose, skip=["pattern_gen"])

    # Apply next patches
    seal5_flow.patch(verbose=verbose, stages=[PatchStage.PHASE_1, PatchStage.PHASE_2])

    # Build patched LLVM
    seal5_flow.build(verbose=verbose, config=build_config, enable_ccache=ccache)

    if not skip_patterns:
        # Build PatternGen & llc
        seal5_flow.build(verbose=verbose, config=build_config, target="pattern-gen", enable_ccache=ccache)
        seal5_flow.build(verbose=verbose, config=build_config, target="llc", enable_ccache=ccache)

        # Generate remaining patches
        seal5_flow.generate(verbose=VERBOSE, only=["pattern_gen"])

        # Apply patches
        seal5_flow.patch(verbose=verbose, stages=list(range(PatchStage.PHASE_3, PatchStage.PHASE_5 + 1)))

    # Build patched LLVM
    seal5_flow.build(verbose=verbose, config=build_config, enable_ccache=ccache)

    if test:
        # Test patched LLVM
        seal5_flow.test(verbose=verbose, ignore_error=ignore_error)

    if install:
        # Install final LLVM
        install_dir = None if out_dir is None else Path(out_dir) / "seal5_llvm_instal"
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

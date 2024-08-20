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
"""PatternGen utils for seal5."""
from pathlib import Path

from seal5.logging import get_logger
from seal5.settings import PatchSettings
from seal5.types import PatchStage
from seal5.index import File, Directory, NamedPatch, write_index_yaml
from seal5 import utils

logger = get_logger()


def build_pattern_gen(
    src: Path, dest: Path, debug: bool = False, use_ninja: bool = False, verbose: bool = False, cmake_options: dict = {}
):
    cmake_args = utils.get_cmake_args(cmake_options)
    dest.mkdir(exist_ok=True)
    utils.cmake(
        src / "llvm",
        *cmake_args,
        use_ninja=use_ninja,
        cwd=dest,
        print_func=logger.info if verbose else logger.debug,
        live=True,
    )
    utils.make(
        "pattern-gen", cwd=dest, print_func=logger.info if verbose else logger.debug, live=True, use_ninja=use_ninja
    )


def get_pattern_gen_patches(
    src: Path,
    temp_dir: Path,
    verbose: bool = False,
):
    # TODO: copy!
    artifacts = []
    directory_artifact = Directory(
        "llvm/tools/pattern-gen",
        src_path=f"{src}/llvm/tools/pattern-gen",
    )
    artifacts.append(directory_artifact)
    file_artifact = File(
        "llvm/include/llvm/CodeGen/GlobalISel/PatternGen.h",
        src_path=f"{src}/llvm/include/llvm/CodeGen/GlobalISel/PatternGen.h",
    )
    artifacts.append(file_artifact)
    file_artifact = File(
        "llvm/lib/CodeGen/GlobalISel/PatternGen.cpp",
        src_path=f"{src}/llvm/lib/CodeGen/GlobalISel/PatternGen.cpp",
    )
    artifacts.append(file_artifact)
    patch_artifact = NamedPatch(
        "llvm/include/llvm/InitializePasses.h",
        key="initialize_passes_decl",
        content="void initializePatternGenPass(PassRegistry&);",
    )
    artifacts.append(patch_artifact)
    patch_artifact = NamedPatch(
        "llvm/lib/CodeGen/GlobalISel/CMakeLists.txt",
        key="gisel_cmake_srcs",
        content="  PatternGen.cpp",
    )
    artifacts.append(patch_artifact)
    patch_artifact = NamedPatch(
        "llvm/lib/CodeGen/GlobalISel/GlobalISel.cpp",
        key="gisel_init",
        content="  initializePatternGenPass(Registry);",
    )
    artifacts.append(patch_artifact)

    index_file = temp_dir / "pattern_gen_support_index.yml"
    write_index_yaml(index_file, artifacts, {}, content=True)
    patch_settings = PatchSettings(
        name="pattern_gen_support",
        stage=int(PatchStage.PHASE_0),
        comment="Integrate PatternGen in Seal5 LLVM",
        index=str(index_file),
        generated=True,
        target="llvm",
    )

    return patch_settings


def build_llc(
    src: Path, dest: Path, debug: bool = False, use_ninja: bool = False, verbose: bool = False, cmake_options: dict = {}
):
    cmake_args = utils.get_cmake_args(cmake_options)
    dest.mkdir(exist_ok=True)
    utils.cmake(
        src / "llvm",
        *cmake_args,
        use_ninja=use_ninja,
        cwd=dest,
        print_func=logger.info if verbose else logger.debug,
        live=True,
    )
    utils.make("llc", cwd=dest, print_func=logger.info if verbose else logger.debug, live=True, use_ninja=use_ninja)


def run_pattern_gen(
    build_dir: Path,
    src: Path,
    dest: Path,
    verbose: bool = False,
    ext=None,
    mattr=None,
    xlen=None,
    skip_formats=False,
    skip_patterns=False,
    skip_verify=True,
    debug=False,
):
    if not isinstance(build_dir, Path):
        build_dir = Path(build_dir)
    pattern_gen_args = [src]
    # pattern_gen_args.extend(["-custom-legalizer-settings=foo", "-disable-gisel-legality-check"])

    if dest:
        pattern_gen_args.extend(["-o", str(dest)])

    if ext:
        # pattern_gen_args.extend(["--ext", ext])
        preds = [f"Has{ext}", f"IsRV{xlen}"]
        preds_str = ", ".join(preds)
        pattern_gen_args.extend(["-p", preds_str])

    if mattr is None:
        attrs = ["+m", "+fast-unaligned-access"]
        if ext:
            ext_ = ext.lower()
            ext_ = ext_.replace("std", "").replace("vendor", "").replace("ext", "")
            attrs.append(f"+{ext_}")
        mattr = ",".join(attrs)

    if mattr:
        pattern_gen_args.extend(["--mattr2", mattr])

    if xlen:
        assert xlen in [32, 64]
        pattern_gen_args.extend(["--riscv-xlen", str(xlen)])

    if skip_patterns:
        pattern_gen_args.append("--skip-patterns")

    if skip_formats:
        pattern_gen_args.append("--skip-formats")

    if skip_verify:
        pattern_gen_args.append("--skip-verify")

    if debug:
        pattern_gen_args.append("--debug")

    # break_on_err = True
    break_on_err = False

    # TODO: dump gmir?
    def handle_exit(code=None, out=None):
        if code is not None and code != 0:
            err_file = str(dest) + ".err"
            with open(err_file, "w") as f:
                f.write(out)
        return code

    pattern_gen_exe = build_dir / "bin" / "pattern-gen"
    assert pattern_gen_exe.is_file(), "pattern-gen not found"

    try:
        out = utils.exec_getout(
            pattern_gen_exe,
            *pattern_gen_args,
            # cwd=dest,
            print_func=logger.info if verbose else logger.debug,
            handle_exit=handle_exit,
            live=True,
        )
    except Exception as e:
        if break_on_err:
            input("^^^ERR^^^")
        if dest.is_file():
            with open(dest, "r") as f:
                content = f.read()
            if len(content) == 0:
                dest.unlink()
        raise e
    if not skip_patterns:
        # errs = None
        # opt_ll = None
        pat = []
        found_pattern = False
        # reason = None
        # rest = []
        is_err = False
        for line in out.split("\n"):
            # print("line", line)
            if found_pattern:
                # print("A1")
                pat.append(line)
                # found_pattern = False
            else:
                # print("A2")
                if "Pattern for" in line:
                    # print("B1")
                    pat = [line.split(":", 1)[1]]
                    # found_pattern = True
                elif "Pattern Generation failed for" in line:
                    # reason = line
                    is_err = True
        print("pat", pat)
        if len(pat) > 0:
            pat = "\n".join(pat)
            pat_file = str(dest) + ".pat"
            with open(pat_file, "w") as f:
                f.write(pat)
        else:
            is_err = True
        # else:
        #     if break_on_err:
        #         print("\n".join(rest))
        #         input("^^^Pattern not found^^^")
        if is_err:
            if break_on_err:
                print(out)
                input("^^^ERROR^^^")
            dest.unlink()
        out_file = str(dest) + (".err" if is_err else ".out")
        with open(out_file, "w") as f:
            f.write(out)
        # if len(rest) > 0:
        #     rest = "\n".join(rest)
        #     rest_file = str(dest) + (".err" if is_err else ".out")
        #     with open(rest_file, "w") as f:
        #         f.write(rest)
        # if reason:
        #     reason_file = str(dest) + ".reason"
        #     with open(reason_file, "w") as f:
        #         f.write(reason)


def convert_ll_to_gmir(
    build_dir: Path,
    src: Path,
    dest: Path,
    mattr=None,
    xlen=None,
    verbose: bool = False,
):
    if mattr is None:
        attrs = ["+m", "+fast-unaligned-access"]
        if xlen == 64 and "+64bit" not in attrs:
            attrs.append("+64bit")
        mattr = ",".join(attrs)

    assert xlen is not None, "Needs XLEN"

    llc_args = [src, f"-mtriple=riscv{xlen}-unknown-elf", "-stop-after=irtranslator", "-global-isel", "-O3"]

    if mattr:
        llc_args.extend(["--mattr", mattr])

    if not isinstance(build_dir, Path):
        build_dir = Path(build_dir)

    llc_exe = build_dir / "bin" / "llc"
    assert llc_exe.is_file(), "llc  not found"

    assert dest is not None
    llc_args.extend(["-o", str(dest)])

    _ = utils.exec_getout(
        llc_exe,
        *llc_args,
        # cwd=dest,
        print_func=logger.info if verbose else logger.debug,
        live=True,
    )

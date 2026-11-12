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

import difflib
import re
import time
from pathlib import Path
from typing import Optional, Union


from seal5.logging import Logger
from seal5.settings import PatchSettings
from seal5.types import PatchStage
from seal5.index import File, Directory, AppendPatch, NamedPatch, write_index_yaml
from seal5.riscv_utils import build_riscv_mattr, get_riscv_defaults
from seal5.tools.pattern_metrics import write_statistics
from seal5 import utils

logger = Logger("tools")


def build_pattern_gen(
    src: Path,
    dest: Path,
    # debug: bool = False,
    use_ninja: bool = False,
    verbose: bool = False,
    cmake_options: Optional[dict] = None,
):
    """Build PatternGen tool."""
    if cmake_options is None:
        cmake_options = {}
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
    # verbose: bool = False,
):
    """Generate patches for PatternGen integration."""
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
    graph_extractor = src / "llvm/lib/CodeGen/GlobalISel/PatternGenGISelTable.cpp"
    has_gisel_table = graph_extractor.is_file()
    if has_gisel_table:
        path = "llvm/lib/CodeGen/GlobalISel/PatternGenGISelTable.cpp"
        artifacts.append(File(path, src_path=str(src / path)))
        tables = "llvm/utils/TableGen/PatternGenTables.inc"
        artifacts.append(File(tables, src_path=str(src / tables)))
    file_artifact = AppendPatch(
        "llvm/include/llvm/IR/IntrinsicsRISCV.td",
        content="""
let TargetPrefix = "riscv" in {
  class PatternGenIntrinsic
    : DefaultAttrsIntrinsic<[llvm_any_ty],
                            [LLVMMatchType<0>],
                            [IntrNoMem, IntrHasSideEffects]>;

  def int_riscv_pg_branch : PatternGenIntrinsic;
}
""",
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
        content="  PatternGen.cpp" + ("\n  PatternGenGISelTable.cpp" if has_gisel_table else ""),
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
        priority=80,
    )

    return patch_settings


def get_pattern_gen_backend_patch(src: Path, llvm_dir: Path, temp_dir: Path):
    """Import backend support from the matching CoreDSL2LLVM release branch.

    Apply before insertion markers so the imported backend retains Seal5's
    extension sites. Older PatternGen branches without ordinary branch support
    continue to use the existing integration.
    """
    target = Path("llvm/lib/Target/RISCV")
    definitions = (src / target / "RISCVInstrInfo.td").read_text()
    operand = re.search(r"def patterngen_btarget\s*:.*?^}\s*$", definitions, re.MULTILINE | re.DOTALL)
    if operand is None:
        return None
    registers = src / target / "RISCVRegisterInfo.td"
    register_text = registers.read_text() if registers.is_file() else ""
    packed_classes = re.findall(r"^def GPR32V[24]\b.*?^}", register_text, re.MULTILINE | re.DOTALL)
    has_packed_simd = len(packed_classes) == 2
    changes = []
    paths = [
        (target / name, name)
        for name in (
            "GISel/RISCVInstructionSelector.cpp",
            "RISCVInstrInfo.cpp",
            "RISCVLateBranchOpt.cpp",
            "RISCVRedundantCopyElimination.cpp",
            "GISel/RISCVLegalizerInfo.cpp",
            "RISCVInstrInfo.td",
        )
    ]
    if has_packed_simd:
        paths.extend(
            (target / name, None)
            for name in (
                "RISCVISelLowering.cpp",
                "RISCVTargetTransformInfo.cpp",
                "RISCVTargetTransformInfo.h",
                "RISCVRegisterInfo.cpp",
                "GISel/RISCVRegisterBankInfo.cpp",
                "GISel/RISCVRegisterBanks.td",
                "Disassembler/RISCVDisassembler.cpp",
            )
        )
        paths.extend(
            [(target / "RISCVRegisterInfo.td", "packed_registers"), (target / "RISCVFeatures.td", "packed_features")]
        )
    if (src / "llvm/lib/CodeGen/GlobalISel/PatternGenGISelTable.cpp").is_file():
        paths.extend(
            (Path(path), None)
            for path in (
                "llvm/include/llvm/CodeGen/GlobalISel/GIMatchTableExecutor.h",
                "llvm/include/llvm/CodeGen/GlobalISel/GIMatchTableExecutorImpl.h",
                "llvm/lib/CodeGen/GlobalISel/GIMatchTableExecutor.cpp",
                "llvm/lib/CodeGen/GlobalISel/InstructionSelect.cpp",
                "llvm/utils/TableGen/GlobalISelEmitter.cpp",
            )
        )
        # LLVM 23 split the matcher implementation out of GlobalISelMatchTable.
        for suffix in ("h", "cpp"):
            matcher = Path(f"llvm/utils/TableGen/Common/GlobalISel/GlobalISelMatchTable.{suffix}")
            if not (src / matcher).is_file():
                matcher = Path(f"llvm/utils/TableGen/Common/GlobalISel/MatchTable/Matchers.{suffix}")
            paths.append((matcher, None))
    for path, name in paths:
        original = (llvm_dir / path).read_text()
        if name == "GISel/RISCVLegalizerInfo.cpp" and not has_packed_simd:
            # Retain the native legalizer; only the extraction marker is needed.
            updated = original.replace(
                "  case Intrinsic::riscv_vsetvli:",
                "  case Intrinsic::riscv_pg_branch:\n  case Intrinsic::riscv_vsetvli:",
                1,
            )
        elif name == "RISCVInstrInfo.td":
            # Seal5 installs its own generated instruction includes.
            updated = original + "\n" + operand.group().rstrip() + "\n"
            if has_packed_simd:
                bridges = re.search(
                    r"// PATTERNGEN_GPR32V_BRIDGES_BEGIN.*?// PATTERNGEN_GPR32V_BRIDGES_END",
                    definitions,
                    re.DOTALL,
                )
                assert bridges is not None, "Missing packed SIMD register-copy patterns"
                updated += bridges.group() + "\n"
        elif name == "packed_registers":
            # Marker patches add an insertion site at EOF. Appending classes
            # here would invalidate that hunk before the marker pass runs.
            anchor = "let RegInfos = XLenRI in {"
            assert original.count(anchor) == 1, "Missing packed-register import anchor"
            updated = original.replace(anchor, "\n\n".join(packed_classes) + "\n\n" + anchor, 1)
        elif name == "packed_features":
            feature_text = (src / path).read_text()
            features = []
            for feature_name in ("FeatureGPR32V", "HasGPR32V", "FeatureGPR32VAdd", "FeatureGPR32VSub"):
                feature = re.search(rf"^def {feature_name}\b.*?;", feature_text, re.MULTILINE | re.DOTALL)
                if feature is None:
                    assert feature_name not in ("FeatureGPR32V", "HasGPR32V"), f"Missing {feature_name}"
                    continue
                features.append(feature.group())
            assert any("hasGPR32V()" in feature for feature in features), "Malformed packed SIMD predicate"
            # TableGen requires these definitions before generated extensions
            # reference them. Preserve the Svinval marker context and EOF too.
            anchor = "def FeatureStdExtSvinval"
            assert original.count(anchor) == 1, "Missing packed-feature import anchor"
            updated = original.replace(anchor, "\n\n".join(features) + "\n\n" + anchor, 1)
        else:
            updated = (src / path).read_text()
        if name == "GISel/RISCVLegalizerInfo.cpp" and has_packed_simd:
            # Removing validation-only markers can leave an extra blank line in
            # the source branch. Keep the native marker insertion context.
            updated = re.sub(
                r"(const LLT nxv16p0 = LLT::scalable_vector\(16, p0\);\n)\n+(?=  using namespace TargetOpcode;)",
                r"\1\n",
                updated,
            )
            updated = re.sub(r"(  using namespace TargetOpcode;\n)\n+(?=  auto BoolVecTys)", r"\1\n", updated)
        changes.extend(
            difflib.unified_diff(
                original.splitlines(keepends=True),
                updated.splitlines(keepends=True),
                fromfile=f"a/{path}",
                tofile=f"b/{path}",
            )
        )
    patch_file = temp_dir / "pattern_gen_backend_support.patch"
    patch_file.write_text("".join(changes))
    return PatchSettings(
        name="pattern_gen_backend_support",
        stage=int(PatchStage.PHASE_0),
        comment="Import PatternGen backend support",
        file=str(patch_file),
        generated=False,  # The diff is already materialized; no index is needed.
        target="llvm",
        priority=95,  # Before insertion markers (90).
    )


def split_minmax_legalizer_actions(source: str) -> str:
    """Give each min/max opcode its own legality rules, preserving all rules.

    Seal5 extends these rules per instruction. LLVM19 uses a named shared
    builder; newer releases use a chained builder with conditional actions.
    """
    pattern = (
        r"(?m)^  (?:auto &(?P<variable>\w+)\s*=\s*)?"
        r"getActionDefinitionsBuilder\(\{G_UMAX, G_UMIN, G_SMAX, G_SMIN\}\)"
    )
    match = re.search(pattern, source)
    if match is None:
        raise ValueError("Cannot find the shared RISC-V min/max legality rules; source preserved")
    variable = match.group("variable")
    terminator = f"{variable}.lower();" if variable else ";"
    end = source.find(terminator, match.end())
    if end < 0:
        raise ValueError("Cannot find the end of the RISC-V min/max legality rules")
    end += len(terminator)
    original = source[match.start() : end]
    single = original.replace(
        "getActionDefinitionsBuilder({G_UMAX, G_UMIN, G_SMAX, G_SMIN})",
        "getActionDefinitionsBuilder(Opcode)",
        1,
    )
    replacement = "  for (unsigned Opcode : {G_UMAX, G_UMIN, G_SMAX, G_SMIN}) {\n"
    replacement += "\n".join("  " + line if line else line for line in single.splitlines())
    replacement += "\n  }"
    return source[: match.start()] + replacement + source[end:]


def get_legalizer_split_patch(llvm_dir: Path, temp_dir: Path) -> Path:
    """Materialize a min/max split against the selected LLVM source version."""
    path = "llvm/lib/Target/RISCV/GISel/RISCVLegalizerInfo.cpp"
    original = (llvm_dir / path).read_text()
    updated = split_minmax_legalizer_actions(original)
    output = temp_dir / "legalizer_split_selected_llvm.patch"
    output.write_text(
        "".join(
            difflib.unified_diff(
                original.splitlines(keepends=True),
                updated.splitlines(keepends=True),
                fromfile="a/" + path,
                tofile="b/" + path,
            )
        )
    )
    return output


def build_llc(
    src: Path,
    dest: Path,
    # debug: bool = False,
    use_ninja: bool = False,
    verbose: bool = False,
    cmake_options: Optional[dict] = None,
):
    """Build llc tool."""
    if cmake_options is None:
        cmake_options = {}
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


def combine_test_fragments(
    ll_file: Union[str, Path],
    instr: str,
    test_header: str,
    test_mir_checks: str,
    test_asm_checks: str,
    return_output=False,
    scalar_inputs=False,
    register_writebacks=0,
):
    with open(ll_file, "r") as f:
        contents = f.read()
    if register_writebacks > 1:
        # PatternGen models register outputs as stores through synthetic noalias
        # pointers. Group their writebacks after the computations, as register
        # results are simultaneous and an early store otherwise blocks fusion.
        stores = list(re.finditer(r"(?m)^  store i\d+ [^,\n]+, ptr (%[\w.]+)[^\n]*\n", contents))
        assert len(stores) == register_writebacks, "Unexpected register-result stores"
        destinations = [store.group(1) for store in stores]
        assert len(set(destinations)) == register_writebacks, "Repeated output pointer"
        header = next(line for line in contents.splitlines() if line.startswith("define "))
        for store, destination in zip(stores, destinations):
            pointer = re.escape(destination)
            assert re.search(r"ptr noalias (?:(?!ptr |%).)*" + pointer + r"(?=[,)])", header), "Output must be noalias"
            assert not re.search(
                r"load [^\n]*ptr " + pointer + r"(?=[,\s])", contents[store.end() :]
            ), "Output read after its writeback"
        writebacks = "".join(store.group() for store in stores)
        for store in reversed(stores):
            contents = contents[: store.start()] + contents[store.end() :]
        assert contents.count("  ret void") == 1, "Expected a single register wrapper"
        contents = contents.replace("  ret void", writebacks + "  ret void", 1)
    if return_output:
        # Return the synthetic register result so a competing store-data rule
        # cannot absorb the arithmetic we intend to test as part of a load.
        result = re.search(r"(?m)^  store (i\d+) ([^,\n]+), ptr [^\n]+\n  ret void$", contents)
        assert result is not None, "Missing final register-result store in pattern-gen IR"
        ty, value = result.groups()
        contents = contents[: result.start()] + f"  ret {ty} {value}" + contents[result.end() :]
        contents = contents.replace("define void @impl", f"define {ty} @impl", 1)
    if scalar_inputs:
        # Register operands should arrive as scalar arguments. Synthetic loads
        # of operand pointers otherwise compete with the memory fusion under
        # test (e.g. a word-load/add can absorb a narrow-load/add's second input).
        contents = scalarize_test_inputs(contents)
    lines = contents.splitlines()
    ret_lines = []
    ret_lines += test_header.splitlines()
    insert_checks = False
    # instr_name = None
    for line in lines:
        if insert_checks:
            insert_checks = False
            # instr_name = None
            ret_lines += test_mir_checks.splitlines()
            ret_lines += test_asm_checks.splitlines()
        if line.startswith("define ") and " @impl" in line:
            insert_checks = True
            # instr_name = line.split("(", 1)[0].split("impl", 1)[-1]
        ret_lines.append(line)
    ret = "\n".join(ret_lines)
    return ret


def scalarize_test_inputs(contents):
    signature = re.search(r"(?m)^define [^\n]+", contents)
    if signature is None:
        raise ValueError("Missing test function signature")
    header = signature.group()
    loads = list(re.finditer(r"(?m)^  (%[\w.]+) = load (i\d+), ptr (%[\w.]+),[^\n]+\n", contents))
    for load in reversed(loads):
        value, ty, pointer = load.groups()
        parameter = r"ptr\b[^,%]*" + re.escape(pointer) + r"(?![\w.])"
        if not re.search(parameter, header):
            continue
        header = re.sub(parameter, ty + " " + pointer, header)
        contents = contents[: load.start()] + contents[load.end() :]
        contents = re.sub(re.escape(value) + r"(?![\w.])", pointer, contents)
    # Edits above only affect the body, so signature offsets remain stable.
    return contents[: signature.start()] + header + contents[signature.end() :]


def run_pattern_gen(
    build_dir: Path,
    src: Path,
    dest: Union[str, Path],
    verbose: bool = False,
    ext=None,
    mattr=None,
    xlen=None,
    skip_formats=False,
    skip_patterns=False,
    skip_verify=True,
    no_extend=True,
    debug=False,
    mnemonic_override=None,
    immediate_operands=None,
    has_register_output=True,
    may_load=False,
    dag_only=False,
    memory_instruction=False,
    gisel_table=False,
    num_register_outputs=None,
):
    """Excute pattern-gen executable."""
    if not isinstance(build_dir, Path):
        build_dir = Path(build_dir)
    if num_register_outputs is None:
        num_register_outputs = int(has_register_output)
    pattern_gen_args = [src]
    if gisel_table:
        pattern_gen_args.append("--gisel-table")
    # pattern_gen_args.extend(["-custom-legalizer-settings=foo", "-disable-gisel-legality-check"])

    if dest:
        if isinstance(dest, str):
            dest = Path(dest)
        assert dest.parent.is_dir(), f"Missing destination directory: {dest}"
        pattern_gen_args.extend(["-o", str(dest)])

    if ext:
        # pattern_gen_args.extend(["--ext", ext])
        preds = [f"Has{ext}", f"IsRV{xlen}"]
        preds_str = ", ".join(preds)
        pattern_gen_args.extend(["-p", preds_str])

    if mattr is None:
        features, _ = get_riscv_defaults()
        if ext:
            ext_ = ext.lower()
            ext_ = ext_.replace("std", "").replace("vendor", "").replace("ext", "")
            features.append(f"+{ext_}")
        mattr = build_riscv_mattr(features, xlen=xlen)

    if mattr:
        pattern_gen_args.extend(["--mattr", mattr])

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

    if no_extend:
        pattern_gen_args.append("--no-extend")
    pattern_gen_args.append("--stats")

    # break_on_err = True
    break_on_err = False

    # TODO: dump gmir?
    returncode = None
    captured_output = ""

    def handle_exit(code=None, out=None):
        nonlocal returncode, captured_output
        returncode = code
        captured_output = out or ""
        if code is not None and code != 0:
            err_file = str(dest) + ".err"
            with open(err_file, "w", encoding="utf-8") as f:
                f.write(out)
        return code

    pattern_gen_exe = build_dir / "bin" / "pattern-gen"
    assert pattern_gen_exe.is_file(), "pattern-gen not found"

    # Write cmd file to easily rerun patterngen
    cmd_str = " ".join(
        map(lambda x: str(x) if str(x).count(" ") == 0 else f"'{x}'", [pattern_gen_exe, *pattern_gen_args])
    )
    cmd_file = str(dest) + ".cmd"
    with open(cmd_file, "w", encoding="utf-8") as f:
        f.write(cmd_str)
    # Remove artifacts from a previous invocation before measuring this one.
    for suffix in (".stats", ".pat", ".err", ".out"):
        Path(str(dest) + suffix).unlink(missing_ok=True)
    dest.unlink(missing_ok=True)
    dest.with_name(dest.stem + "InstrFormat" + dest.suffix).unlink(missing_ok=True)
    dest.with_suffix(".inc.patch").unlink(missing_ok=True)
    if gisel_table:
        dest.with_suffix(".inc").unlink(missing_ok=True)
    started = time.perf_counter()
    out = ""
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
            with open(dest, "r", encoding="utf-8") as f:
                content = f.read()
            if len(content) == 0:
                dest.unlink()
        raise e
    finally:
        write_statistics(
            dest,
            out or captured_output,
            time.perf_counter() - started,
            gisel_table,
            skip_patterns,
            returncode,
            skip_formats=skip_formats,
        )
    if not skip_patterns:
        # errs = None
        # opt_ll = None
        patterns = []
        found_pattern = False
        # reason = None
        # rest = []
        num_err = 0
        instr = None
        mnemonic = None

        pattern_re = re.compile(r"^Pattern for\s+(?P<instr>\S+)(?:\s+\[(?P<mnemonic>[^\]]+)\])?\s*:\s*(?P<pattern>.*)$")

        pat = []
        for line in out.split("\n"):
            # print("line", line)
            if len(line.strip()) == 0 or line.startswith("==="):
                continue
            if found_pattern and "Pattern for" not in line:
                # print("A1")
                pat.append(line)
                # found_pattern = False
            else:
                # print("A2")
                if "Pattern for" in line:
                    if found_pattern:
                        pattern = "\n".join(pat)
                        patterns.append(pattern)
                        pat = []
                        found_pattern = False
                    match_ = pattern_re.match(line.strip())
                    # print("match_", match_)
                    if not match_:
                        raise ValueError(f"Could not parse pattern line: {line!r}")

                    instr_ = match_.group("instr")
                    # print("instr", instr)
                    mnemonic_ = match_.group("mnemonic")  # None when [...] is absent
                    # print("mnemonic_", mnemonic_)
                    pattern = match_.group("pattern")
                    # print("pattern", pattern)
                    assert instr_ is not None
                    if instr is None:
                        instr = instr_
                    else:
                        # unroll_imm patterns can have a suffix
                        # TODO: fix
                        # assert instr == instr_ or instr_.startswith(
                        #     f"{instr}_"
                        # ), f"Expected same instr: {instr} vs. {instr_}"
                        pass
                    if mnemonic_ is not None:
                        if mnemonic is None:
                            mnemonic = mnemonic_
                        else:
                            assert mnemonic == mnemonic_, f"Expected same mnemonic: {mnemonic} vs. {mnemonic_}"
                    pat = [pattern]
                    # print("instr", instr)
                    # print("mnemonic", mnemonic)
                    # print("pat", pat)
                    found_pattern = True
                elif "Pattern Generation failed for" in line:
                    # reason = line
                    num_err += 1
                # if "Pattern for" in line:
                #     # print("B1")
                #     instr_ = line.split(":", 1)[0].split(" ")[-1]
                #     if instr is None:
                #         instr = instr_
                #     else:
                #         assert instr == instr_, f"Expected same instr: {instr} vs. {instr_}"
                #     mnemonic = "TODO"
                #     pat = [line.split(":", 1)[1]]
                #     # found_pattern = True
        if found_pattern:
            pattern = "\n".join(pat)
            patterns.append(pattern)
            pat = []
            found_pattern = False
        ll_files = []
        has_imm = False
        # print("pat", pat, len(pat))
        num_patterns = len(patterns)
        # print("patterns", patterns, num_patterns)
        has_err = num_err > 0
        # print("has_err", has_err)
        is_fatal_err = num_patterns == 0
        # print("is_fatal_err", is_fatal_err)
        if num_patterns > 0:
            pat_file = str(dest) + ".pat"
            patterns_str = "\n".join(patterns)
            with open(pat_file, "w", encoding="utf-8") as f:
                f.write(patterns_str)

            uses_strs = []
            for pattern in patterns:

                uses = re.compile(r":\$([^:\s(),]*)").findall(pattern)
                assert len(uses) > 0
                uses = list(set(uses))
                uses_str_ = ",".join(uses)
                uses_strs.append(uses_str_)
                has_imm_ = (
                    bool(set(uses) & set(immediate_operands)) if immediate_operands is not None else "imm" in uses_str_
                )
                has_imm |= has_imm_
            uses_str = "\n".join(uses_strs)

            uses_file = str(dest) + ".uses"
            with open(uses_file, "w", encoding="utf-8") as f:
                f.write(uses_str)
            ll_file = str(dest).replace(".td", ".ll")
            assert Path(ll_file).is_file(), f"LLVM-IR file not found: {ll_file}"
            ll_files.append(ll_file)
        if mnemonic_override is not None:
            mnemonic = mnemonic_override
        generate_tests = "auto"
        if generate_tests == "auto":
            generate_tests = not has_imm and mnemonic is not None and not has_err
        assert isinstance(generate_tests, bool)
        test_files = []
        if generate_tests:
            # print("ll_files", ll_files)
            assert instr is not None
            assert mnemonic is not None
            # TODO: optimize?
            # TODO: generate patterns for each xlen
            # TODO: get real mnemonic
            # mnemonic = instr.lower()
            # TODO: get real llvm instr name
            llvm_instr = instr
            # TODO: move to different pass
            # TODO: make optional
            if xlen is None:
                xlens = [32, 64]
            else:
                xlens = [xlen]
            packed_register_output = bool(re.search(r"\(outs\s+GPR32V[24]:", dest.read_text()))
            test_header = ""
            test_mir_checks = ""
            test_asm_checks = ""
            for xlen in xlens:
                store_mir = "SD" if xlen == 64 else "SW"
                store_asm = store_mir.lower()
                selector = "-global-isel=0" if dag_only else "-global-isel=1 -global-isel-abort=1"
                selected_pass = "finalize-isel" if dag_only else "instruction-select"
                test_header += (
                    f"; RUN: llc -mtriple=riscv{xlen} -stop-after={selected_pass} "
                    f"-mattr={mattr} %s {selector} -o - \\\n"
                    f"  ; RUN: | FileCheck -check-prefix=RV{xlen}-MIR %s\n"
                    f"  ; RUN: llc -mtriple=riscv{xlen} -mattr={mattr} %s "
                    f"{selector} -o - \\\n"
                    f"  ; RUN: | FileCheck -check-prefix=RV{xlen}-ASM %s\n"
                )
                if memory_instruction and not dag_only:
                    test_header += (
                        f"; RUN: llc -mtriple=riscv{xlen} -stop-after=finalize-isel "
                        f"-mattr={mattr} %s -global-isel=0 -o - \\\n"
                        f"  ; RUN: | FileCheck -check-prefix=RV{xlen}-MIR %s\n"
                        f"; RUN: llc -mtriple=riscv{xlen} -mattr={mattr} %s "
                        f"-global-isel=0 -o - \\\n"
                        f"  ; RUN: | FileCheck -check-prefix=RV{xlen}-ASM %s\n"
                    )
                test_mir_checks += f"  ; RV{xlen}-MIR-LABEL: name: impl{instr}\n"
                # test_mir_checks += f"  ; RV{xlen}-MIR: LW\n"  # TODO: once per reg input operand
                test_mir_checks += f"  ; RV{xlen}-MIR: {llvm_instr}\n"
                if has_register_output and not may_load:
                    # Packed results may cross a register-class COPY before the scalar writeback.
                    store_check = "MIR" if packed_register_output else "MIR-NEXT"
                    test_mir_checks += f"  ; RV{xlen}-{store_check}: {store_mir}\n" * num_register_outputs
                ret_check = "MIR" if may_load and has_register_output else "MIR-NEXT"
                test_mir_checks += f"  ; RV{xlen}-{ret_check}: PseudoRET\n"
                test_asm_checks += f"  ; RV{xlen}-ASM-LABEL: impl{instr}:\n"
                # test_asm_checks += f"  ; RV{xlen}-ASM: lw\n"  # TODO: once per reg input operand
                test_asm_checks += f"  ; RV{xlen}-ASM: {mnemonic}\n"
                if has_register_output and not may_load:
                    test_asm_checks += f"  ; RV{xlen}-ASM-NEXT: {store_asm}\n" * num_register_outputs
                ret_check = "ASM" if may_load and has_register_output else "ASM-NEXT"
                test_asm_checks += f"  ; RV{xlen}-{ret_check}: ret\n"
            # print("test_header", test_header)
            # print("test_mir_checks", test_mir_checks)
            # print("test_asm_checks", test_asm_checks)
            assert len(ll_files) == 1
            ll_file = ll_files[0]
            test_content = combine_test_fragments(
                ll_file,
                instr,
                test_header,
                test_mir_checks,
                test_asm_checks,
                return_output=may_load and has_register_output,
                scalar_inputs=memory_instruction,
                register_writebacks=num_register_outputs if gisel_table else 0,
            )
            # print("test_content", test_content)
            test_file = ll_file.replace(".ll", ".test-cg.ll")
            with open(test_file, "w") as f:
                f.write(test_content)
            test_files += [test_file]
        # input(">")
        # print("G")
        # else:
        #     if break_on_err:
        #         print("\n".join(rest))
        #         input("^^^Pattern not found^^^")
        if is_fatal_err:
            if break_on_err:
                print(out)
                input("^^^ERROR^^^")
            dest.unlink()
        out_file = str(dest) + (".err" if is_fatal_err else ".out")
        with open(out_file, "w", encoding="utf-8") as f:
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
        return test_files


def convert_ll_to_gmir(
    build_dir: Path,
    src: Path,
    dest: Path,
    mattr=None,
    xlen=None,
    optimize=3,
    verbose: bool = False,
):
    """Convert LLVM-IR file to GMIR file."""
    if mattr is None:
        features, _ = get_riscv_defaults()
        mattr = build_riscv_mattr(features, xlen=xlen)

    assert xlen is not None, "Needs XLEN"

    llc_args = [src, f"-mtriple=riscv{xlen}-unknown-elf", "-stop-after=irtranslator", "-global-isel", f"-O{optimize}"]

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


def lower_branch_patterns_to_riscv(contents):
    """Match the target BR_CC node produced by RISC-V's BRCOND lowering.

    PatternGen describes generic brcond/setcc trees. RISC-V custom-lowers those
    before DAG selection, including swapping greater-than comparisons. Keep
    these rules out of the GlobalISel importer.
    """

    def arguments(text):
        depth, start, result = 0, 0, []
        for index, char in enumerate(text):
            depth += (char == "(") - (char == ")")
            if char == "," and depth == 0:
                result.append(text[start:index].strip())
                start = index + 1
        result.append(text[start:].strip())
        return result

    def untype(text):
        match = re.fullmatch(r"\(i(?:32|64)\s+(.*)\)", text, re.S)
        return match.group(1).strip() if match else text

    offset = 0
    while True:
        match = re.search(r"\(brcond\s+", contents[offset:])
        if match is None:
            break
        start = offset + match.start()
        depth, end = 1, start + 1
        while end < len(contents) and depth:
            depth += (contents[end] == "(") - (contents[end] == ")")
            end += 1
        if depth:
            raise ValueError("Unbalanced branch TableGen pattern")
        condition, target = arguments(contents[start + len("(brcond") : end - 1])
        condition = untype(condition)
        if not condition.startswith("(setcc ") or not condition.endswith(")"):
            raise ValueError("Expected a setcc condition in a generated branch pattern")
        lhs, rhs, cc = arguments(condition[len("(setcc ") : -1])
        swaps = {"SETGT": "SETLT", "SETLE": "SETGE", "SETUGT": "SETULT", "SETULE": "SETUGE"}
        if cc in swaps:
            lhs, rhs, cc = rhs, lhs, swaps[cc]
        if cc not in ("SETEQ", "SETNE", "SETLT", "SETGE", "SETULT", "SETUGE"):
            raise ValueError(f"Unsupported branch condition {cc}")
        replacement = f"(riscv_brcc {lhs}, {rhs}, {cc}, {target})"
        contents = contents[:start] + replacement + contents[end:]
        offset = start + len(replacement)
    return ignore_gisel_patterns(contents)


def ignore_gisel_patterns(contents):
    """Scope the importer exclusion to Pattern records, preserving helpers."""
    return re.sub(r"(?m)^([ \t]*)def\s*:\s*Pat\s*<", r"\1let GISelShouldIgnore = 1 in def : Pat<", contents)

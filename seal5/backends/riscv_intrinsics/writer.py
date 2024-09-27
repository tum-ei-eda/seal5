# SPDX-License-Identifier: Apache-2.0
#
# This file is part of the M2-ISA-R project: https://github.com/tum-ei-eda/M2-ISA-R
#
# Copyright (C) 2022
# Chair of Electrical Design Automation
# Technical University of Munich

"""Clean M2-ISA-R/Seal5 metamodel to .core_desc file."""

import argparse
import logging
import pathlib
import pickle
import os.path
from typing import Union
from dataclasses import dataclass

from m2isar.metamodel import arch

from seal5.index import NamedPatch, write_index_yaml
from seal5.settings import IntrinsicDefn

logger = logging.getLogger("riscv_intrinsics")


def ir_type_to_text(ir_type: str):
    # needs fleshing out with all likely types
    # probably needs to take into account RISC-V bit width, e.g. does "Li" means 32 bit integer on a 128-bit platform?
    if ir_type == "i32":
        return "Li"
    raise NotImplementedError(f'Unhandled ir_type "{ir_type}"')


def build_target(arch: str, intrinsic: IntrinsicDefn):
    # Target couples intrinsic name to argument types and function behaviour
    # Start with return type if not void
    arg_str = ""
    if intrinsic.ret_type:
        arg_str += ir_type_to_text(intrinsic.ret_type)
    for arg in intrinsic.args:
        arg_str += ir_type_to_text(arg.arg_type)

    target = f'TARGET_BUILTIN(__builtin_{arch}_{intrinsic.intrinsic_name}, "{arg_str}", "nc", "{arch}")'
    return target


def ir_type_to_pattern(ir_type: str):
    # needs fleshing out with all likely types
    if ir_type == "i32":
        return "llvm_i32_ty"
    raise NotImplementedError(f'Unhandled ir_type "{ir_type}"')


def build_attr(arch: str, intrinsic: IntrinsicDefn):
    uses_mem = False  # @todo
    attr = f"  def int_riscv_{intrinsic.intrinsic_name} : Intrinsic<\n    ["
    if intrinsic.ret_type:
        attr += f"{ir_type_to_pattern(intrinsic.ret_type)}"
    attr += "],\n    ["
    for idx, arg in enumerate(intrinsic.args):
        if idx:
            attr += ", "
        attr += ir_type_to_pattern(arg.arg_type)
    attr += "],\n"
    attr += "    [IntrNoMem, IntrSpeculatable, IntrWillReturn]>;"
    return attr


def build_emit(arch: str, intrinsic: IntrinsicDefn):
    emit = (
        f"  case RISCV::BI__builtin_{arch}_{intrinsic.intrinsic_name}:\n"
        f"    ID = Intrinsic::riscv_{intrinsic.intrinsic_name};\n"
        f"    break;"
    )
    return emit


@dataclass
class PatchFrag:
    """Pairs patch contents to location to apply it"""

    patchee: str
    tag: str
    contents: str = ""


def main():
    """Main app entrypoint."""

    # read command line args
    parser = argparse.ArgumentParser()
    parser.add_argument("top_level", help="A .m2isarmodel or .seal5model file.")
    parser.add_argument("--log", default="info", choices=["critical", "error", "warning", "info", "debug"])
    parser.add_argument("--output", "-o", type=str, default=None)
    parser.add_argument("--splitted", action="store_true", help="Split per set")
    parser.add_argument("--formats", action="store_true", help="Also generate instruction formats")
    parser.add_argument("--metrics", default=None, help="Output metrics to file")
    parser.add_argument("--index", default=None, help="Output index to file")
    parser.add_argument("--ext", type=str, default="td", help="Default file extension (if using --splitted)")
    args = parser.parse_args()

    # initialize logging
    logging.basicConfig(level=getattr(logging, args.log.upper()))

    # resolve model paths
    top_level = pathlib.Path(args.top_level)

    is_seal5_model = False
    if top_level.suffix == ".seal5model":
        is_seal5_model = True
    if args.output is None:
        assert top_level.suffix in [".m2isarmodel", ".seal5model"], "Can not infer model type from file extension."
        raise NotImplementedError

        # out_path = top_level.parent / (top_level.stem + ".core_desc")
    else:
        out_path = pathlib.Path(args.output)

    logger.info("intrinsics/writer - loading models")
    if not is_seal5_model:
        raise NotImplementedError

    # load models
    with open(top_level, "rb") as f:
        # models: "dict[str, arch.CoreDef]" = pickle.load(f)
        if is_seal5_model:
            model: "dict[str, Union[arch.InstructionSet, ...]]" = pickle.load(f)
            model["cores"] = {}
        else:  # TODO: core vs. set!
            temp: "dict[str, Union[arch.InstructionSet, arch.CoreDef]]" = pickle.load(f)
            assert len(temp) > 0, "Empty model!"
            if isinstance(list(temp.values())[0], arch.CoreDef):
                model = {"cores": temp, "sets": {}}
            elif isinstance(list(temp.values())[0], arch.InstructionSet):
                model = {"sets": temp, "cores": {}}
            else:
                assert False

    metrics = {
        "n_sets": 0,
        "n_skipped": 0,
        "n_failed": 0,
        "n_success": 0,
    }
    # preprocess model
    # print("model", model)
    artifacts = {}
    artifacts[None] = []  # used for global artifacts
    if args.splitted:
        raise NotImplementedError
    else:
        # errs = []
        settings = model.get("settings", None)
        llvm_version = None
        if not settings or not settings.intrinsics.intrinsics:
            logger.warning("No intrinsics configured; didn't need to invoke intrinsics writer.")
            quit()
        if settings:
            llvm_settings = settings.llvm
            if llvm_settings:
                llvm_state = llvm_settings.state
                if llvm_state:
                    llvm_version = llvm_state.version  # unused today, but needed very soon
        patch_frags = {
            "target": PatchFrag(patchee="clang/include/clang/Basic/BuiltinsRISCV.def", tag="builtins_riscv"),
            "attr": PatchFrag(patchee="llvm/include/llvm/IR/IntrinsicsRISCV.td", tag="intrinsics_riscv"),
            "emit": PatchFrag(patchee="clang/lib/CodeGen/CGBuiltin.cpp", tag="cg_builtin"),
        }
        for set_name, set_def in model["sets"].items():
            artifacts[set_name] = []
            metrics["n_sets"] += 1
            ext_settings = set_def.settings
            if ext_settings is None:
                metrics["n_skipped"] += 1
                continue
            for intrinsic in settings.intrinsics.intrinsics:
                metrics["n_success"] += 1

                patch_frags["target"].contents += build_target(arch=ext_settings.get_arch(), intrinsic=intrinsic)
                patch_frags["attr"].contents += build_attr(arch=ext_settings.get_arch(), intrinsic=intrinsic)
                patch_frags["emit"].contents += build_emit(arch=ext_settings.get_arch(), intrinsic=intrinsic)

        for id, frag in patch_frags.items():
            contents = frag.contents
            if len(contents) > 0:
                if id == "target":
                    contents = f"// {ext_settings.get_arch()}\n{contents}\n"
                elif id == "attr":
                    contents = f'let TargetPrefix = "riscv" in {{\n{contents}\n}}'
                (root, ext) = os.path.splitext(out_path)
                patch_path = root + "_" + id + ext
                with open(patch_path, "w") as f:
                    f.write(contents)
                key = frag.tag
                if ext_settings.experimental:
                    key += "_experimental"
                patch = NamedPatch(frag.patchee, key=key, src_path=patch_path, content=contents)
                artifacts[None].append(patch)
    if args.metrics:
        metrics_file = args.metrics
        with open(metrics_file, "w") as f:
            f.write(",".join(metrics.keys()))
            f.write("\n")
            f.write(",".join(map(str, metrics.values())))
            f.write("\n")
    if args.index:
        if sum(map(lambda x: len(x), artifacts.values())) > 0:
            global_artifacts = artifacts.get(None, [])
            set_artifacts = {key: value for key, value in artifacts.items() if key is not None}
            index_file = args.index
            write_index_yaml(index_file, global_artifacts, set_artifacts, content=True)
        else:
            logger.warning("No patches generated. No index file will be written.")


if __name__ == "__main__":
    main()

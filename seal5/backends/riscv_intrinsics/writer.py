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
import os.path
from typing import Optional
from dataclasses import dataclass

import pandas as pd

from seal5.index import NamedPatch, write_index_yaml
from seal5.settings import IntrinsicDefn
from seal5.model_utils import load_model

logger = logging.getLogger("riscv_intrinsics")


# See https://github.com/llvm-mirror/clang/blob/master/include/clang/Basic/Builtins.def
# Types:
#  v -> void
#  b -> boolean
#  c -> char
#  s -> short
#  i -> int
#  h -> half
#  f -> float
#  d -> double
#  z -> size_t
#  w -> wchar_t
#  F -> constant CFString
#  G -> id
#  H -> SEL
#  M -> struct objc_super
#  a -> __builtin_va_list
#  A -> "reference" to __builtin_va_list
#  V -> Vector, followed by the number of elements and the base type.
#  E -> ext_vector, followed by the number of elements and the base type.
#  X -> _Complex, followed by the base type.
#  Y -> ptrdiff_t
#  P -> FILE
#  J -> jmp_buf
#  SJ -> sigjmp_buf
#  K -> ucontext_t
#  p -> pid_t
#  . -> "...".  This may only occur at the end of the function list.
#
# Types may be prefixed with the following modifiers:
#  L   -> long (e.g. Li for 'long int', Ld for 'long double')
#  LL  -> long long (e.g. LLi for 'long long int', LLd for __float128)
#  LLL -> __int128_t (e.g. LLLi)
#  Z   -> int32_t (require a native 32-bit integer type on the target)
#  W   -> int64_t (require a native 64-bit integer type on the target)
#  N   -> 'int' size if target is LP64, 'L' otherwise.
#  O   -> long for OpenCL targets, long long otherwise.
#  S   -> signed
#  U   -> unsigned
#  I   -> Required to constant fold to an integer constant expression.
#
# Types may be postfixed with the following modifiers:
# * -> pointer (optionally followed by an address space number, if no address
#               space is specified than any address space will be accepted)
# & -> reference (optionally followed by an address space number)
# C -> const
# D -> volatile
#

IR_TYPE_LOOKUP_TEXT = {
    # "i32": "Li",
    "i1": "b",
    "i8": "c",
    "i16": "s",
    "i32": "Zi",
    "i64": "Wi",
    "f16": "h",
    "f32": "f",
    "f64": "d",
    # TODO: sign?
}

IR_TYPE_LOOKUP_PREFIX = {
    (None,): "U",
    (False,): "U",
    (True,): "S",
}


def ir_type_lookup_new(llvm_ty, signed: bool):
    ret = None
    if llvm_ty in ["i1"]:
        ret = "bool"
    elif llvm_ty in ["i64", "i32", "i16", "i8"]:
        sz = int(llvm_ty[1:])
        ret = f"int{sz}_t"
        if not signed:
            ret = f"u{ret}"
    elif llvm_ty in ["f64", "f32", "f16"]:
        sz = int(llvm_ty[1:])
        lookup = {
            16: "half",
            32: "float",  # single
            64: "double",
        }
        ret = lookup[sz]
    if ret is None:
        raise NotImplementedError("Unhandled llvm type: {llvm_ty}")
    return ret


IR_TYPE_LOOKUP_PAT = {
    # TODO: use f"llvm_{ir_type}_ty" instead?
    "i1": "llvm_i1_ty",
    "i8": "llvm_i8_ty",
    "i16": "llvm_i16_ty",
    "i32": "llvm_i32_ty",
    "i64": "llvm_i64_ty",
    "f16": "llvm_half_ty",
    "f32": "llvm_float_ty",
    "f64": "llvm_double_ty",
    # llvm_anyint_ty?
    # llvm_anyvector_ty?
    # llvm_ptr_ty?
}


def ir_type_to_text(ir_type: str, signed: bool = False, legacy: bool = True):
    # TODO: needs fleshing out with all likely types
    # TODO: probably needs to take into account RISC-V bit width, e.g. does "Li"
    #   means 32 bit integer on a 128-bit platform?
    if legacy:
        prefix_lookup = IR_TYPE_LOOKUP_PREFIX
        # print("prefix_lookup", prefix_lookup)
        # print("signed", signed, type(signed))
        key = (signed,)
        # print("key", key)
        prefix_found = prefix_lookup.get(key, None)
        assert prefix_found is not None, f"Unhandled prefix for ir_type '{ir_type}'"
        text_lookup = IR_TYPE_LOOKUP_TEXT
        found = text_lookup.get(ir_type, None)
        assert found is not None, f"Unhandled ir_type '{ir_type}'"
        return found
    ret = ir_type_lookup_new(ir_type, signed)
    assert ret is not None
    return ret


def build_target(arch: str, intrinsic: IntrinsicDefn):
    # Target couples intrinsic name to argument types and function behaviour
    # Start with return type if not void
    arg_str = ""
    if intrinsic.ret_type:
        arg_str += ir_type_to_text(intrinsic.ret_type, signed=intrinsic.ret_signed, legacy=True)
    for arg in intrinsic.args:
        arg_str += ir_type_to_text(arg.arg_type, signed=arg.signed, legacy=True)

    target = f'TARGET_BUILTIN(__builtin_riscv_{arch}_{intrinsic.intrinsic_name}, "{arg_str}", "nc", "{arch}")\n'
    return target


def build_target_new(
    arch: str, intrinsic: IntrinsicDefn, prefix: Optional[str] = "__builtin_riscv", xlen: Optional[int] = None
):
    attributes = ["NoThrow", "Const"]  # TODO: expose/use/group
    if prefix != "__builtin_riscv":
        # Use: let Spellings = ["__builtin_riscv_" # NAME];
        raise NotImplementedError("Clang builtin custom prefix")
    ret_str = "void"
    if intrinsic.ret_type:
        ret_str = ir_type_to_text(intrinsic.ret_type, signed=intrinsic.ret_signed, legacy=False)
    args_str = ", ".join([ir_type_to_text(arg.arg_type, signed=arg.signed, legacy=False) for arg in intrinsic.args])
    prototype_str = f"{ret_str}({args_str})"
    features = [arch]
    if xlen is not None:
        features.append(f"{xlen}bit")
    features_str = ",".join(features)
    target = f'def {arch}_{intrinsic.intrinsic_name} : RISCVBuiltin<"{prototype_str}", "{features_str}">;'
    if len(attributes) > 0:
        attributes_str = ", ".join(attributes)
        ret = f"""let Attributes = [{attributes_str}] in {{
{target}
}} // Attributes = [{attributes_str}]
"""
    else:
        ret = f"{target}\n"

    return ret


def ir_type_to_pattern(ir_type: str):
    # needs fleshing out with all likely types
    found = IR_TYPE_LOOKUP_PAT.get(ir_type, None)
    assert found is not None, f"Unhandled ir_type '{ir_type}'"
    return found


def build_attr(arch: str, intrinsic: IntrinsicDefn):
    # uses_mem = False  # TODO: use
    attr = f"  def int_riscv_{arch}_{intrinsic.intrinsic_name} : Intrinsic<\n    ["
    if intrinsic.ret_type:
        attr += f"{ir_type_to_pattern(intrinsic.ret_type)}"
    attr += "],\n    ["
    for idx, arg in enumerate(intrinsic.args):
        if idx:
            attr += ", "
        attr += ir_type_to_pattern(arg.arg_type)
    attr += "],\n"
    attr += "    [IntrNoMem, IntrSpeculatable, IntrWillReturn]>;\n"
    return attr


def build_emit(arch: str, intrinsic: IntrinsicDefn):
    emit = (
        f"  case RISCV::BI__builtin_riscv_{arch}_{intrinsic.intrinsic_name}:\n"
        f"    ID = Intrinsic::riscv_{arch}_{intrinsic.intrinsic_name};\n"
        f"    break;\n"
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
    parser.add_argument("--ignore-failing", action="store_true", help="Do not crash in case of errors.")
    parser.add_argument("--compat", action="store_true")
    args = parser.parse_args()

    # initialize logging
    logging.basicConfig(level=getattr(logging, args.log.upper()))

    # resolve model paths
    top_level = pathlib.Path(args.top_level)
    out_path = pathlib.Path(args.output)

    model_obj = load_model(top_level, compat=args.compat)

    metrics = {
        "n_sets": 0,
        "n_instructions": 0,
        "n_intrinsics": 0,
        "n_skipped": 0,
        "n_failed": 0,
        "n_success": 0,
        "skipped_instrinsics": [],
        "failed_intrinsics": [],
        "success_intrinsics": [],
        "skipped_instructions": [],
        "failed_instructions": [],
        "success_instructions": [],
        "skipped_sets": [],
        "failed_sets": [],
        "success_sets": [],
    }
    # preprocess model
    # print("model", model)
    artifacts = {}
    artifacts[None] = []  # used for global artifacts
    if args.splitted:
        raise NotImplementedError
    else:
        # errs = []
        settings = model_obj.settings
        llvm_version = None
        if not settings or not settings.intrinsics.intrinsics:
            logger.warning("No intrinsics configured; didn't need to invoke intrinsics writer.")
            quit()  # TODO: refactor this
        if settings:
            llvm_settings = settings.llvm
            if llvm_settings:
                llvm_state = llvm_settings.state
                if llvm_state:
                    llvm_version = llvm_state.version  # unused today, but needed very soon
                    assert llvm_version.major >= 17
        patch_frags = {
            "attr": PatchFrag(patchee="llvm/include/llvm/IR/IntrinsicsRISCV.td", tag="intrinsics_riscv"),
            "emit": PatchFrag(patchee="clang/lib/CodeGen/CGBuiltin.cpp", tag="cg_builtin"),
        }
        if llvm_version is not None and llvm_version.major < 19:
            patch_frags["target"] = PatchFrag(
                patchee="clang/include/clang/Basic/BuiltinsRISCV.def", tag="builtins_riscv"
            )
        else:
            patch_frags["target"] = PatchFrag(
                patchee="clang/include/clang/Basic/BuiltinsRISCV.td", tag="builtins_riscv"
            )
        global_riscv_settings = settings.riscv
        model_name = top_level.stem
        model_settings = settings.models.get(model_name)
        model_riscv_settings = model_settings.riscv
        riscv_settings = global_riscv_settings
        if model_riscv_settings is not None:
            riscv_settings = riscv_settings.merge(model_riscv_settings)
        for set_name, _ in model_obj.sets.items():
            artifacts[set_name] = []
            metrics["n_sets"] += 1
            # ext_settings = set_def.settings
            ext_settings = model_settings.extensions.get(set_name)
            riscv_settings_ = riscv_settings
            ext_riscv_settings = ext_settings.riscv
            if ext_riscv_settings:
                riscv_settings_ = riscv_settings.merge(ext_riscv_settings)

            if ext_settings is None or len(settings.intrinsics.intrinsics) == 0:
                metrics["n_skipped"] += 1
                metrics["skipped_sets"].append(set_name)
                continue
            assert riscv_settings_ is not None
            xlen = riscv_settings_.xlen
            assert xlen is not None
            for intrinsic in settings.intrinsics.intrinsics:
                if intrinsic.set_name is not None and intrinsic.set_name != set_name:
                    continue
                try:
                    arch_ = ext_settings.get_arch(name=set_name)
                    if llvm_version is not None and llvm_version.major < 19:
                        patch_frags["target"].contents += build_target(arch=arch_, intrinsic=intrinsic)
                    else:
                        patch_frags["target"].contents += build_target_new(arch=arch_, intrinsic=intrinsic, xlen=xlen)
                    patch_frags["attr"].contents += build_attr(arch=arch_, intrinsic=intrinsic)
                    patch_frags["emit"].contents += build_emit(arch=arch_, intrinsic=intrinsic)
                    metrics["n_success"] += 1
                    metrics["success_instructions"].append(intrinsic.instr_name)
                except Exception as ex:
                    logger.exception(ex)
                    metrics["n_failed"] += 1
                    metrics["failed_instructions"].append(intrinsic.instr_name)
                    # metrics["failed_intrinsics"].append(?)
            metrics["success_sets"].append(set_name)

        for id, frag in patch_frags.items():
            contents = frag.contents
            if len(contents) > 0:
                if id == "target":
                    contents = f"// {arch_}\n{contents}\n"
                elif id == "attr":
                    contents = f'let TargetPrefix = "riscv" in {{\n{contents}\n}}'
                (root, ext) = os.path.splitext(out_path)
                patch_path = root + "_" + id + ext
                with open(patch_path, "w") as f:
                    f.write(contents.strip())
                key = frag.tag
                patch = NamedPatch(frag.patchee, key=key, src_path=patch_path, content=contents.strip())
                artifacts[None].append(patch)
    if not args.ignore_failing:
        n_failed = metrics["n_failed"]
        if n_failed > 0:
            failed = metrics["failed_instructions"]
            failing_str = ", ".join(failed)
            logger.error("%s intructions failed: %s", n_failed, failing_str)
            raise RuntimeError("Abort due to errors")
    if args.metrics:
        metrics_file = args.metrics
        metrics_df = pd.DataFrame({key: [val] for key, val in metrics.items()})
        metrics_df.to_csv(metrics_file, index=False)
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

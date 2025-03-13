# SPDX-License-Identifier: Apache-2.0
#
# This file is part of the M2-ISA-R project: https://github.com/tum-ei-eda/M2-ISA-R
#
# Copyright (C) 2022
# Chair of Electrical Design Automation
# Technical University of Munich

"""Create LLVM patches for new field types."""

import re
import argparse
import logging
import pathlib

from seal5.index import write_index_yaml, NamedPatch

from seal5.settings import Seal5Settings

logger = logging.getLogger("riscv_field_types")

SEAL5_RISCV_FIELDS_SUPPORT = """class Seal5RISCVUImmOp<int bitsNum> : RISCVOp {
  let ParserMatchClass = UImmAsmOperand<bitsNum>;
  let DecoderMethod = "decodeUImmOperand<" # bitsNum # ">";
  let OperandType = "SEAL5_OPERAND_UIMM" # bitsNum;
}
class Seal5RISCVUImmLeafOp<int bitsNum> :
  Seal5RISCVUImmOp<bitsNum>, ImmLeaf<XLenVT, "return isUInt<" # bitsNum # ">(Imm);">;
class Seal5RISCVSImmOp<int bitsNum> : RISCVOp {
  let ParserMatchClass = SImmAsmOperand<bitsNum>;
  let EncoderMethod = "getImmOpValue";
  let DecoderMethod = "decodeSImmOperand<" # bitsNum # ">";
  let OperandType = "SEAL5_OPERAND_SIMM" # bitsNum;
}
class Seal5RISCVSImmLeafOp<int bitsNum> :
  Seal5RISCVSImmOp<bitsNum>, ImmLeaf<XLenVT, "return isInt<" # bitsNum # ">(Imm);">;
"""


def gen_riscv_field_types_str(field_types):
    # print("gen_riscv_field_types_str", field_types)
    riscv_field_types_contents = [SEAL5_RISCV_FIELDS_SUPPORT] if len(field_types) > 0 else []
    riscv_operands_asm_contents = []
    riscv_operands_enum_contents = []

    for field_type in field_types:
        # print("field_type", field_type)
        matches = re.compile(r"([us])imm(\d+|log2xlen)([_a-zA-Z].*)?").match(field_type)
        assert matches is not None, f"Field type not supported: {field_type}"
        # print("matches", matches)
        groups = list(matches.groups())
        sign_letter, imm_size, suffix = groups
        # print("sign_letter", sign_letter)
        # print("imm_size", imm_size)
        # print("suffix", suffix)
        assert sign_letter in ["u", "s"]
        assert imm_size.isdigit()
        imm_size = int(imm_size)
        assert suffix is None  # TODO: handle suffixes
        # TODO: leaf or not?
        is_leaf = True
        if sign_letter == "u":
            cls = "Seal5RISCVUImmLeafOp" if is_leaf else "Seal5RISCVUImmOp"
            temp = f"def {field_type} : {cls}<{imm_size}>;"
        elif sign_letter == "s":
            cls = "Seal5RISCVSImmLeafOp" if is_leaf else "Seal5RISCVSImmOp"
            # Warning: RISCVSImmOp not tested yet
            temp = f"""def {field_type} : {cls}<{imm_size}> {{
  let MCOperandPredicate = [{{
    int64_t Imm;
    if (MCOp.evaluateAsConstantImm(Imm))
      return isInt<{imm_size}>(Imm);
    return MCOp.isBareSymbolRef();
  }}];
}}"""
        else:
            assert False  # Should not be reached
        riscv_field_types_contents.append(temp)
        sign_letter_upper = sign_letter.upper()
        if sign_letter_upper == "U":
            temp = (
                f"bool is{sign_letter_upper}Imm{imm_size}() const {{ return Is{sign_letter_upper}Imm<{imm_size}>(); }}"
            )
        elif sign_letter_upper == "S":
            # TODO: introduce `template <unsigned N> bool IsSImm() const {`
            # to make this more clean
            temp = f"""bool is{sign_letter_upper}Imm{imm_size}() const {{
      if (!isImm())
        return false;
      RISCVMCExpr::VariantKind VK = RISCVMCExpr::VK_RISCV_None;
      int64_t Imm;
      bool IsConstantImm = evaluateConstantImm(getImm(), Imm, VK);
      return IsConstantImm && isInt<{imm_size}>(fixImmediateForRV32(Imm, isRV64Imm())) &&
             VK == RISCVMCExpr::VK_RISCV_None;
    }}"""
        else:
            assert False  # Should not be reached
        riscv_operands_asm_contents.append(temp)
        field_type_upper = field_type.upper()
        temp = f"  SEAL5_OPERAND_{field_type_upper},"
        riscv_operands_enum_contents.append(temp)

    riscv_field_types_content = "\n".join(riscv_field_types_contents)
    riscv_operands_asm_content = "\n".join(riscv_operands_asm_contents)
    riscv_operands_enum_content = "\n".join(riscv_operands_enum_contents)
    return riscv_field_types_content, riscv_operands_asm_content, riscv_operands_enum_content


def main():
    """Main app entrypoint."""

    # read command line args
    parser = argparse.ArgumentParser()
    # parser.add_argument("top_level", help="A .m2isarmodel or .seal5model file.")  # TODO: drop?
    parser.add_argument("--log", default="info", choices=["critical", "error", "warning", "info", "debug"])
    parser.add_argument("--output", "-o", type=str, default=None)
    parser.add_argument("--metrics", default=None, help="Output metrics to file")
    parser.add_argument("--index", default=None, help="Output index to file")
    parser.add_argument("--ext", type=str, default="td", help="Default file extension (if using --splitted)")
    parser.add_argument("--compat", action="store_true")
    parser.add_argument("--yaml", type=str, default=None)
    args = parser.parse_args()

    # initialize logging
    logging.basicConfig(level=getattr(logging, args.log.upper()))

    # resolve model paths
    # top_level = pathlib.Path(args.top_level)
    assert args.yaml is not None
    assert pathlib.Path(args.yaml).is_file()
    settings = Seal5Settings.from_yaml_file(args.yaml)

    # print("settings", settings)
    # print("settings.models", settings.models)
    # print("settings.models['Example']", settings.models["Example"])
    # print("settings.models['Example'].extensions", settings.models["Example"].extensions)
    # print("settings.models['Example'].extensions['XExample']", settings.models["Example"].extensions["XExample"])
    # print(
    #     "settings.models['Example'].extensions['XExample'].required_imm_types",
    #     settings.models["Example"].extensions["XExample"].required_imm_types,
    # )
    # print("settings.models", settings.models)
    all_required_imm_types = set(
        sum(
            [
                ext_settings.required_imm_types
                for model_name, model_settings in settings.models.items()
                for ext_name, ext_settings in model_settings.extensions.items()
                if ext_settings.required_imm_types is not None
            ],
            [],
        )
    )
    # print("all_required_imm_types", all_required_imm_types)
    supported_imm_types = set(settings.llvm.state.supported_imm_types)
    # print("supported_imm_types", supported_imm_types)
    missing_imm_types = all_required_imm_types - supported_imm_types
    # print("missing_imm_types", missing_imm_types)

    metrics = {
        "n_imm": 0,
        "n_skipped": 0,
        "n_failed": 0,
        "n_success": 0,
    }
    # preprocess model
    # print("model", model)
    # settings = model.get("settings", None)
    artifacts = {}
    artifacts[None] = []  # used for global artifacts
    # TODO: error handling?
    if len(missing_imm_types) > 0:
        field_types_content, riscv_operands_asm_content, riscv_operands_enum_content = gen_riscv_field_types_str(
            missing_imm_types
        )
    else:
        field_types_content, riscv_operands_asm_content, riscv_operands_enum_content = "", "", ""
    metrics["n_imm"] = len(missing_imm_types)
    metrics["n_success"] = len(missing_imm_types)
    # print("field_types_content", field_types_content)
    # print("riscv_operands_asm_content", riscv_operands_asm_content)
    # print("riscv_operands_enum_content", riscv_operands_enum_content)
    if len(field_types_content) > 0:
        field_types_patch = NamedPatch(
            "llvm/lib/Target/RISCV/RISCVInstrInfo.td",
            key="field_types",  # TODO: rename: riscv_field_types
            content=field_types_content,
        )
        artifacts[None].append(field_types_patch)
    if len(riscv_operands_asm_content) > 0:
        riscv_operands_asm_patch = NamedPatch(
            "llvm/lib/Target/RISCV/AsmParser/RISCVAsmParser.cpp",
            key="riscv_operands",  # TODO: rename: riscv_operands_asm
            content=riscv_operands_asm_content,
        )
        artifacts[None].append(riscv_operands_asm_patch)
    if len(riscv_operands_enum_content) > 0:
        riscv_operands_enum_patch = NamedPatch(
            "llvm/lib/Target/RISCV/MCTargetDesc/RISCVBaseInfo.h",
            key="riscv_operands",  # TODO: rename: riscv_operands_enum
            content=riscv_operands_enum_content,
        )
        artifacts[None].append(riscv_operands_enum_patch)
    # input("!!!")
    if args.metrics:
        metrics_file = args.metrics
        with open(metrics_file, "w", encoding="utf-8") as f:
            f.write(",".join(metrics.keys()))
            f.write("\n")
            f.write(",".join(map(str, metrics.values())))
            f.write("\n")
    if args.index:
        if sum(map(len, artifacts.values())) > 0:
            global_artifacts = artifacts.get(None, [])
            set_artifacts = {key: value for key, value in artifacts.items() if key is not None}
            index_file = args.index
            write_index_yaml(index_file, global_artifacts, set_artifacts, content=True)
        else:
            logger.warning("No patches generated. No index file will be written.")


if __name__ == "__main__":
    main()

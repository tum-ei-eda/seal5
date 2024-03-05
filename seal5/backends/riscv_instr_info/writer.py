# SPDX-License-Identifier: Apache-2.0
#
# This file is part of the M2-ISA-R project: https://github.com/tum-ei-eda/M2-ISA-R
#
# Copyright (C) 2022
# Chair of Electrical Design Automation
# Technical University of Munich

"""Clean M2-ISA-R/Seal5 metamodel to .core_desc file."""

import re
import argparse
import logging
import pathlib
import pickle
from typing import Union

from mako.template import Template

from m2isar.metamodel import arch

from seal5.index import NamedPatch, File, write_index_yaml
# from seal5.settings import ExtensionsSettings
from seal5.model import Seal5OperandAttribute, Seal5InstrAttribute

from .templates import template_dir

logger = logging.getLogger("riscv_instr_info")


# MAKO_TEMPLATE = """def Feature${predicate} : SubtargetFeature<"${arch}", "Has${predicate}", "true", "'${feature}' (${description})">;
#
# def Has${predicate} : Predicate<"Subtarget->has${predicate}()">, AssemblerPredicate<(any_of Feature${predicate}), "'${feature}' (${description})">;"""

class Operand:
    def __init__(self, name, lower, upper):
        self.name = name
        # self._name = name
        self.lower = lower
        self.upper = upper

    @property
    def length(self):
        return (self.upper - self.lower + 1) if self.upper >= self.lower else (self.lower - self.upper + 1)

    # @property
    # def name(self):
    #   ty, name_ = self._name.split(":")
    #   if self.lower == 1:
    #       ty += "_lsb0"
    #   ret = f"{ty}:{name_}"
    #   return ret

    def __repr__(self):
        return f"Operand({self.name}, {self.lower}, {self.upper})"


class EncodingField:
    def __init__(self, name, start, length, value=None, extra=None):
        self.name = name
        self.start = start
        self.length = length

        self.value = value
        self.const = value is not None
        self.extra = extra if extra is not None else value

    def __repr__(self):
        return f"EncodingField({self.name}, {self.start}, {self.length}, {self.value}, {self.const})"


def process_encoding(enc):
    # print("get_encoding", enc)
    operands = {}
    for e in reversed(enc):
        if isinstance(e, arch.BitField):
            name = e.name
            if name in operands:
                op = operands[name]
                op.lower = min(e.range.lower, op.lower)
                op.upper = max(e.range.upper, op.upper)
            else:
                op = Operand(name, e.range.lower, e.range.upper)
                operands[name] = op
    fields = []
    start = 0
    for e in reversed(enc):
        if isinstance(e, arch.BitField):
            name = e.name
            assert name in operands
            op = operands[name]
            if op.length > e.range.length:
                if e.range.length == 1:
                    name = name + "{" + str(e.range.lower - op.lower) + "}"
                else:
                    name = name + "{" + str(e.range.upper - op.lower) + "-" + str(e.range.lower - op.lower) + "}"
            new = EncodingField(name, start, e.range.length)
            start += e.range.length
        elif isinstance(e, arch.BitVal):
            # lower = 0
            new = EncodingField(None, start, e.length, e.value)
            start += e.length
        else:
            assert False
        fields.insert(0, new)
    # print("fields", fields)
    # input(">")
    return operands.values(), fields


def write_riscv_instruction_info(name, real_name, asm_str, ins_str, outs_str, enc, fields, operands, details_str, attrs={}, constraints=[], formats=False):

    if formats:
        instr_template = Template(filename=str(template_dir/'instr_tablegen2.mako'))
    else:
        instr_template = Template(filename=str(template_dir/'instr_tablegen.mako'))

    operands, fields = process_encoding(enc)

    attrs = {key: int(value) if isinstance(value, bool) else value for key, value in attrs.items()}
    constraints_str = ", ".join(constraints)

    out_str = instr_template.render(name=name, real_name=real_name, xlen=32, asm_str=asm_str, ins_str=ins_str, outs_str=outs_str, sched_str=str([]), operands=operands, fields=fields, attrs=attrs, constraints_str=constraints_str)

    if len(details_str) > 0:
        out_str = details_str + " in {\n" + "\n".join([("  " + line) if len(line) > 0 else line for line in out_str.split("\n")]) + "\n} // " + details_str + "\n"

    logger.info("writing TableGen for instruction %s", name)

    return out_str


def gen_riscv_instr_info_str(instr):
    print("instr", instr)
    name = instr.name
    operands = instr.operands
    print("operands", operands)
    reads = []
    writes = []
    for op_name, op in operands.items():
        print("op", op)
        print("op.constraints", op.constraints)
        if len(op.constraints) > 0:
            raise NotImplementedError
        print("op.attributes", op.attributes)
        if Seal5OperandAttribute.IS_REG in op.attributes:
            assert Seal5OperandAttribute.REG_CLASS in op.attributes
            cls = op.attributes[Seal5OperandAttribute.REG_CLASS]
            assert cls in ["GPR"]
            pre = cls
        elif Seal5OperandAttribute.IS_IMM in op.attributes:
            assert Seal5OperandAttribute.TY in op.attributes
            ty = op.attributes[Seal5OperandAttribute.TY]
            assert ty[0] in ["u", "s"]
            sz = int(ty[1:])
            pre = f"{ty}imm{sz}"

        if Seal5OperandAttribute.OUT in op.attributes and Seal5OperandAttribute.IN in op.attributes:
            op_str2 = f"{pre}:${op_name}_wb"
            writes.append(op_str2)
            op_str = f"{pre}:${op_name}"
            reads.append(op_str)
        elif Seal5OperandAttribute.OUT in op.attributes:
            op_str = f"{pre}:${op_name}"
            writes.append(op_str)
        elif Seal5OperandAttribute.IN in op.attributes:
            op_str = f"{pre}:${op_name}"
            reads.append(op_str)
    print("reads", reads)
    print("writes", writes)
    attributes = instr.attributes
    print("attributes", attributes)
    real_name = instr.mnemonic
    asm_str = instr.assembly
    asm_str = re.sub(r'{([a-zA-Z0-9]+)}', r'$\g<1>', re.sub(r'{([a-zA-Z0-9]+):[#0-9a-zA-Z\.]+}', r'{\g<1>}', re.sub(r'name\(([a-zA-Z0-9]+)\)', r'\g<1>', asm_str)))
    print("asm_str_orig", asm_str)
    asm_order = re.compile(r"(\$[a-zA-Z0-9]+)").findall(asm_str)
    print("asm_order", asm_order)
    for op in asm_order:
        if f"{op}(" in asm_str or f"{op})" in asm_str or f"{op}!" in asm_str or f"!{op}" in asm_str:
            asm_str = asm_str.replace(op, "${" + op[1:] + "}")
    print("asm_str_new", asm_str)
    reads_ = [(x.split(":", 1)[1] if ":" in x else x) for x in reads]
    print("reads_", reads_)
    writes_ = [(x.split(":", 1)[1] if ":" in x else x).replace("_wb", "") for x in writes]
    print("writes_", writes_)

    ins_str = ", ".join([reads[reads_.index(x)] for x in asm_order if x in reads_])
    print("ins_str", ins_str)
    outs_str = ", ".join([writes[writes_.index(x)] for x in asm_order if x in writes_])
    print("outs_str", outs_str)
    details_str = ""
    fields = instr.fields
    print("fields")
    encoding = instr.encoding
    print("encoding")
    # input(">")
    attrs = {}
    if Seal5InstrAttribute.HAS_SIDE_EFFECTS in attributes:
        attrs["hasSideEffects"] = 1
    if Seal5InstrAttribute.MAY_LOAD in attributes:
        attrs["mayLoad"] = 1
    if Seal5InstrAttribute.MAY_STORE in attributes:
        attrs["mayStore"] = 1
    if Seal5InstrAttribute.IS_TERMINATOR in attributes:
        attrs["isTerminator"] = 1
    constraints = instr.constraints
    if len(constraints) > 0:
        raise NotImplementedError
    formats = True
    tablegen_str = write_riscv_instruction_info(name, real_name, asm_str, ins_str, outs_str, encoding, fields, operands, details_str, attrs=attrs, constraints=constraints, formats=formats)
    return tablegen_str


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
    # abs_top_level = top_level.resolve()

    is_seal5_model = False
    # print("top_level", top_level)
    # print("suffix", top_level.suffix)
    if top_level.suffix == ".seal5model":
        is_seal5_model = True
    if args.output is None:
        assert top_level.suffix in [".m2isarmodel", ".seal5model"], "Can not infer model type from file extension."
        raise NotImplementedError

        # out_path = top_level.parent / (top_level.stem + ".core_desc")
    else:
        out_path = pathlib.Path(args.output)

    logger.info("loading models")
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
    # settings = model.get("settings", None)
    artifacts = {}
    artifacts[None] = []  # used for global artifacts
    if args.splitted:
        content = ""
        # errs = []
        includes = []
        for set_name, set_def in model["sets"].items():
            set_name_lower = set_name.lower()
            artifacts[set_name] = []
            set_dir = out_path / set_name
            set_dir.mkdir(exist_ok=True)
            ext_settings = set_def.settings
            pred = None
            if ext_settings is not None:
                pred = "Has" + ext_settings.get_predicate(name=set_name)
            metrics["n_sets"] += 1
            for instr_name, instr_def in set_def.instructions.items():
                metrics["n_success"] += 1
                out_name = f"{instr_def.name}InstrInfo.{args.ext}"
                output_file = set_dir / out_name
                content += gen_riscv_instr_info_str(instr_def)
                if len(content) > 0:
                    assert pred is not None
                    predicate_str = f"Predicates = [{pred}, IsRV32]"
                    content = f"let {predicate_str} in{{\n{content}\n}}"
                    with open(output_file, "w") as f:
                        f.write(content)
                    instr_info_patch = File(
                        f"llvm/lib/Target/RISCV/seal5/{set_name}/{output_file.name}", src_path=output_file,
                    )
                    artifacts[set_name].append(instr_info_patch)
                    inc = f"seal5/{set_name}/{output_file.name}"
                    includes.append(inc)

            includes_str = "\n".join([f"include \"{inc}\"" for inc in includes])
            set_td_includes_patch = NamedPatch(
                f"llvm/lib/Target/RISCV/seal5/{set_name}.td", key=f"{set_name_lower}_set_td_includes", content=includes_str,
            )
            artifacts[set_name].append(set_td_includes_patch)
    else:
        raise NotImplementedError
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

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
from typing import Union

from mako.template import Template

from m2isar.metamodel import arch

from seal5.index import NamedPatch, File, write_index_yaml

# from seal5.settings import ExtensionsSettings

from .templates import template_dir

logger = logging.getLogger("riscv_instr_info")


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


def write_riscv_instruction_info(
    name,
    real_name,
    asm_str,
    ins_str,
    outs_str,
    enc,
    fields,
    # operands,
    size,
    details_str,
    attrs={},
    constraints=[],
    formats=False,
    compressed_pat=None,
):
    if formats:
        instr_template = Template(filename=str(template_dir / "instr_tablegen2.mako"))
    else:
        instr_template = Template(filename=str(template_dir / "instr_tablegen.mako"))

    operands, fields = process_encoding(enc)

    attrs = {key: int(value) if isinstance(value, bool) else value for key, value in attrs.items()}
    constraints_str = ", ".join(constraints)

    out_str = instr_template.render(
        name=name,
        real_name=real_name,
        size=size,
        asm_str=asm_str,
        ins_str=ins_str,
        outs_str=outs_str,
        sched_str=str([]),
        operands=operands,
        fields=fields,
        attrs=attrs,
        constraints_str=constraints_str,
    )
    if compressed_pat:
        out_str += f"\n{compressed_pat}"

    if len(details_str) > 0:
        out_str = (
            details_str
            + " in {\n"
            + "\n".join([("  " + line) if len(line) > 0 else line for line in out_str.split("\n")])
            + "\n} // "
            + details_str
            + "\n"
        )

    logger.info("writing TableGen for instruction %s", name)

    return out_str


def gen_riscv_instr_info_str(instr, set_def):
    print("instr", instr)
    name = instr.name
    # operands = instr.operands
    size = instr.size
    # print("operands", operands)
    reads = instr.llvm_reads
    writes = instr.llvm_writes
    constraints = instr.llvm_constraints
    print("reads", reads)
    print("writes", writes)
    constraints = instr.llvm_constraints
    print("constraints", constraints)
    # constraints_str = ", ".join(constraints)
    attributes = instr.attributes
    print("attributes", attributes)
    real_name = instr.mnemonic
    asm_str = instr.llvm_asm_str
    print("asm_str", asm_str)
    ins_str = instr.llvm_ins_str
    print("ins_str", ins_str)
    outs_str = instr.llvm_outs_str
    print("outs_str", outs_str)
    details_str = ""
    fields = instr.fields
    print("fields")
    encoding = instr.encoding
    print("encoding")
    attrs = instr.llvm_attributes
    # constraints = instr.constraints
    # if len(constraints) > 0:
    #     raise NotImplementedError
    formats = True
    compressed_pat = instr.llvm_get_compressed_pat(set_def)
    tablegen_str = write_riscv_instruction_info(
        name,
        real_name,
        asm_str,
        ins_str,
        outs_str,
        encoding,
        fields,
        # operands,
        size,
        details_str,
        attrs=attrs,
        constraints=constraints,
        formats=formats,
        compressed_pat=compressed_pat,
    )
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
        for set_name, set_def in model["sets"].items():
            set_name_lower = set_name.lower()
            artifacts[set_name] = []
            xlen = set_def.xlen
            includes = []
            set_dir = out_path / set_name
            set_dir.mkdir(exist_ok=True)
            ext_settings = set_def.settings
            pred = None
            if ext_settings is not None:
                pred = "Has" + ext_settings.get_predicate(name=set_name)
            metrics["n_sets"] += 1
            # TODO: check for GPRC and require HasStdExtCOrZca?
            # TODO: check for GPR32Pair and require HasGPR32Pair
            # TODO: check for GPR32V2/GPR32V4 and require HasGPR32V
            for instr_name, instr_def in set_def.instructions.items():
                metrics["n_success"] += 1
                out_name = f"{instr_def.name}InstrInfo.{args.ext}"
                output_file = set_dir / out_name
                content = gen_riscv_instr_info_str(instr_def, set_def)
                if len(content) > 0:
                    assert pred is not None
                    predicate_str = f"Predicates = [{pred}, IsRV{xlen}]"
                    content = f"let {predicate_str} in {{\n{content}\n}}"
                    with open(output_file, "w") as f:
                        f.write(content)
                    instr_info_patch = File(
                        f"llvm/lib/Target/RISCV/seal5/{set_name}/{output_file.name}",
                        src_path=output_file,
                    )
                    artifacts[set_name].append(instr_info_patch)
                    inc = f"seal5/{set_name}/{output_file.name}"
                    includes.append(inc)

            includes_str = "\n".join([f'include "{inc}"' for inc in includes])
            set_td_includes_patch = NamedPatch(
                f"llvm/lib/Target/RISCV/seal5/{set_name}.td",
                key=f"{set_name_lower}_set_td_includes",
                content=includes_str,
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

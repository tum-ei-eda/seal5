# SPDX-License-Identifier: Apache-2.0
#
# This file is part of the M2-ISA-R project: https://github.com/tum-ei-eda/M2-ISA-R
#
# Copyright (C) 2022
# Chair of Electrical Design Automation
# Technical University of Munich

"""Clean M2-ISA-R/Seal5 metamodel to .core_desc file."""

import copy
import argparse
import logging
import pathlib
import pickle
from typing import Union

from . import visitor
from m2isar.metamodel import arch, behav, patch_model

logger = logging.getLogger("coredsl2_writer")


class CoreDSL2Writer:
    # def __init__(self, compat=False):
    def __init__(self, compat=True, version="coredsl2"):
        self.version = version
        self.compat = compat  # Reduced syntax for cdsl2llvm parser
        self.text = ""
        self.indent_str = "    "
        self.level = 0

    @property
    def is_seal5(self):
        # TODO: use this
        return self.version == "seal5"

    @property
    def is_coredsl2(self):
        return self.version == "coredsl2"

    @property
    def indent(self):
        return self.indent_str * self.level

    @property
    def isstartofline(self):
        return len(self.text) == 0 or self.text[-1] == "\n"

    @property
    def needsspace(self):
        return len(self.text) != 0 and self.text[-1] not in ["\n", " "]

    def write(self, text, nl=False):
        # print("text", text, type(text))
        if isinstance(text, int):
            text = str(text)
        assert isinstance(text, str)
        lines = text.split("\n")
        for i, line in enumerate(lines):
            if self.isstartofline:
                self.text += self.indent
            self.text += line
            if (i < len(lines) - 1) or nl:
                self.text += "\n"

    def write_line(self, text):
        self.write(text, nl=True)

    def enter_block(self, br=True, nl=True):
        if br:
            if self.needsspace:
                self.write(" ")
            self.write("{", nl=nl)
        self.level += 1

    def leave_block(self, br=True, nl=True):
        assert self.level > 0
        self.level -= 1
        if br:
            self.write("}", nl=nl)

    def write_type(self, data_type, size):
        # print("write_type")
        # print("data_type", data_type)
        # print("size", size)
        if data_type == arch.DataType.U:
            self.write("unsigned")
        elif data_type == arch.DataType.S:
            self.write("signed")
        elif data_type == arch.DataType.NONE:
            self.write("void")
        else:
            raise NotImplementedError(f"Unsupported type: {data_type}")
        if size:
            self.write("<")
            self.write(size)
            self.write(">")

    def write_attribute(self, attr, val=None):
        if self.needsspace:
            self.write(" ")
        if val is not None:
            if isinstance(val, list) and len(val) == 0:
                val = None
        if self.compat and val is not None:
            return
        self.write("[[")
        self.write(attr.name.lower())
        if val is not None:
            self.write("=")

            def helper(val):
                if isinstance(val, list):  # TODO: replace with string literal
                    if len(val) == 1:
                        return helper(val[0])
                    return "(" + ",".join([helper(x) for x in val]) + ")"
                elif isinstance(val, str):  # TODO: replace with string literal
                    return val  # TODO: operation
                elif isinstance(val, int):  # TODO: replace with int literal
                    return str(val)  # TODO: operation
                elif isinstance(val, behav.IntLiteral):
                    return str(val.value)
                elif isinstance(val, behav.StringLiteral):
                    return val.value
                else:
                    raise NotImplementedError(f"Unhandled case: {type(val)}")

            val = helper(val)
            self.write(val)
        self.write("]]")
        # print("key", key)
        # print("value", value)

    def write_attributes(self, attributes):
        for attr, val in attributes.items():
            self.write_attribute(attr, val)
        # input("inp")

    def write_function(self, function):
        if function.static:
            self.write("static ")
        if function.extern:
            self.write("extern ")
        self.write_type(function.data_type, None)  # TODO: size?
        self.write(" ")
        self.write(function.name)
        self.write("(")
        for i, param in enumerate(function.args.values()):
            self.write_type(param.data_type, param.size)
            self.write(" ")
            self.write(param.name)
            if i < len(function.args) - 1:
                self.write(", ")
        self.write(")")
        self.write_attributes(function.attributes)
        # self.enter_block()
        # self.write_behavior(instruction)
        if function.extern:
            self.write_line(";")
        else:
            function.operation.generate(self)
        # self.leave_block()

    def write_functions(self, functions):
        if self.compat:
            return
        self.write("functions")
        # TODO: attributes
        self.enter_block()
        for function in functions.values():
            self.write_function(function)
        self.leave_block()

    def write_encoding_val(self, bitval):
        value = bitval.value
        width = bitval.length
        self.write(width)
        self.write("'b")
        bitstr = bin(value)[2:].zfill(width)
        self.write(bitstr)

    def write_encoding_field(self, bitfield):
        name = bitfield.name
        rng = bitfield.range
        # print("rng", rng)
        # input("aaaa")
        self.write(name)
        self.write(f"[{rng.upper}:{rng.lower}]")

    def write_operand(self, operand):
        self.write_type(operand.ty.datatype, operand.ty.width)
        self.write(" ")
        self.write(operand.name)
        self.write_attributes(operand.attributes)
        self.write_line(";")

    def write_constraints(self, constraints):
        for constraint in constraints:
            # print("constraint", constraint, type(constraint), dir(constraint))
            for stmt in constraint.stmts:
                stmt.generate(self)
                desc = constraint.description
                if desc:
                    self.write(f";  // {desc}", nl=True)
                else:
                    self.write(";", nl=True)

    def write_instruction_constraints(self, constraints, operands):
        if self.compat:
            return
        self.write("constraints: ")
        if len(constraints) == 0:
            self.write_line("{};")
            return
        self.enter_block()
        op_constraints = sum([op.constraints for op in operands.values()], [])
        self.write_constraints(op_constraints)
        self.write_constraints(constraints)
        self.leave_block()

    def write_operands(self, operands):
        self.write("operands: ")
        if len(operands) == 0:
            self.write_line("{}")
            return
        self.enter_block()
        # print("operands", operands)
        for i, op in enumerate(operands.values()):
            self.write_operand(op)
        # for i, op in enumerate(operands.values()):
        #     self.write_constraints(op.constraints)
        self.leave_block()

    def write_encoding(self, encoding):
        self.write("encoding: ")
        # print("encoding", encoding, dir(encoding))
        for i, elem in enumerate(encoding):
            if isinstance(elem, arch.BitVal):
                self.write_encoding_val(elem)
            elif isinstance(elem, arch.BitField):
                self.write_encoding_field(elem)
            else:
                assert False
            if i < len(encoding) - 1:
                self.write(" :: ")
        self.write(";", nl=True)

    def write_assembly(self, instruction):
        self.write("assembly: ")
        mnemonic = instruction.mnemonic
        assembly = instruction.assembly
        if mnemonic and not self.compat:
            self.write("{")
            self.write(f'"{mnemonic}"')
            self.write(", ")
        if assembly is None:
            assembly = ""
        self.write(f'"{assembly}"')
        if mnemonic and not self.compat:
            self.write("}")
        self.write(";", nl=True)

    def write_behavior(self, instruction):
        self.write("behavior: ")
        op = instruction.operation
        if self.compat:
            self.enter_block()
        op.generate(self)
        if self.compat:
            self.leave_block()
        # self.write(";", nl=True)

    def write_instruction(self, instruction):
        # print("write_instruction", instruction)
        self.write(instruction.name)
        self.write_attributes(instruction.attributes)
        self.enter_block()
        self.write_operands(instruction.operands)  # seal5 only
        self.write_instruction_constraints(instruction.constraints, instruction.operands)  # seal5 only
        self.write_encoding(instruction.encoding)
        self.write_assembly(instruction)
        self.write_behavior(instruction)
        self.leave_block()

    def write_instructions(self, instructions):
        # print("write_instructions", instructions)
        self.write("instructions")
        # TODO: attributes?
        self.enter_block()
        for instruction in instructions.values():
            self.write_instruction(instruction)
        self.leave_block()

    def write_architectural_state(self, set_def):
        self.write("architectural_state")
        # print("set_def", set_def, dir(set_def))
        self.enter_block()
        # TODO: scalars, memories,...
        self.leave_block()

    def write_set(self, set_def):
        # print("write_set", set_def)
        # self.write_architectural_state()
        self.write("InstructionSet ")
        self.write(set_def.name)
        # TODO: attributes
        # TODO: extends
        if set_def.extension:
            self.write(" extends ")
            self.write(", ".join(set_def.extension))
        self.enter_block()
        self.write_functions(set_def.functions)
        self.write_instructions(set_def.instructions)
        self.leave_block()

    #     for instr_name, instr_def in set_def.instructions.items():
    #         logger.debug("writing instr %s", instr_def.name)
    #         # instr_def.operation.generate(context)
    #     # input("CONT1")


def main():
    """Main app entrypoint."""

    # read command line args
    parser = argparse.ArgumentParser()
    parser.add_argument("top_level", help="A .m2isarmodel or .seal5model file.")
    parser.add_argument("--log", default="info", choices=["critical", "error", "warning", "info", "debug"])
    parser.add_argument("--output", "-o", type=str, default=None)
    parser.add_argument("--compat", action="store_true", help="Generate pattern-gen compatible syntax")
    parser.add_argument("--splitted", action="store_true", help="Split per set and instruction")
    parser.add_argument("--ext", type=str, default="core_desc", help="Default file extension (if using --splitted)")
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

        out_path = top_level.parent / (top_level.stem + ".core_desc")
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

    # preprocess model
    # print("model", model)
    if args.splitted:
        assert out_path.is_dir(), "Expecting output directory when using --splitted"
        for set_name, set_def in model["sets"].items():
            for instr_def in set_def.instructions.values():
                writer = CoreDSL2Writer(compat=args.compat)
                logger.debug("writing instr %s/%s", set_def.name, instr_def.name)
                patch_model(visitor)
                set_def_ = copy.deepcopy(set_def)
                set_def_.instructions = {
                    key: instr_def
                    for key, instr_def_ in set_def.instructions.items()
                    if instr_def.name == instr_def_.name
                }
                # TODO: drop_ununsed
                writer.write_set(set_def_)
                content = writer.text
                out_path_ = out_path / set_name / f"{instr_def.name}.{args.ext}"
                out_path_.parent.mkdir(exist_ok=True)
                with open(out_path_, "w") as f:
                    f.write(content)
    else:
        writer = CoreDSL2Writer(compat=args.compat)
        for set_name, set_def in model["sets"].items():
            # print("set", set_def)
            # print("instrs", set_def.instructions)
            # input("123")
            logger.debug("writing set %s", set_def.name)
            patch_model(visitor)
            writer.write_set(set_def)
        content = writer.text
        with open(out_path, "w") as f:
            f.write(content)


if __name__ == "__main__":
    main()

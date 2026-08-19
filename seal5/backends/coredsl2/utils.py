# SPDX-License-Identifier: Apache-2.0
#
# This file is part of the M2-ISA-R project: https://github.com/tum-ei-eda/M2-ISA-R
#
# Copyright (C) 2022
# Chair of Electrical Design Automation
# Technical University of Munich

"""Clean M2-ISA-R/Seal5 metamodel to .core_desc file."""

from typing import Optional, Set

from m2isar.backends.coredsl2.utils import CoreDSL2Writer
from m2isar.metamodel import arch, behav
from m2isar.metamodel.type_info import TypeKind

from seal5.logging import Logger
from seal5.model import DataType

logger = Logger("backends.coredsl2_writer")


class Seal5CoreDSL2Writer(CoreDSL2Writer):

    def __init__(
        self,
        visitor,
        reduced: bool = True,
        skip_empty: bool = False,
        drop_first_op: bool = False,
        allowed_attrs: Optional[Set[str]] = None,
        version="coredsl2",
    ):
        super().__init__(
            visitor, reduced=reduced, skip_empty=skip_empty, drop_first_op=drop_first_op, allowed_attrs=allowed_attrs
        )
        self.version = version
        self.level = 0

    @property
    def is_seal5(self):
        return self.version == "seal5"

    @property
    def is_coredsl2(self):
        return self.version == "coredsl2"

    def write_type(self, ty):
        if hasattr(ty, "kind"):
            super().write_type(ty)
            return
        if hasattr(ty, "datatype"):
            kind_map = {
                DataType.NONE: TypeKind.NONE,
                DataType.U: TypeKind.UINT,
                DataType.S: TypeKind.INT,
                DataType.F: TypeKind.FLOAT,
                DataType.D: TypeKind.FLOAT,
                DataType.Q: TypeKind.FLOAT,
                DataType.B: TypeKind.UINT,
            }
            kind = kind_map.get(ty.datatype)
            if kind is None:
                raise NotImplementedError(f"Unsupported Seal5 datatype: {ty.datatype}")
            if kind in (TypeKind.INT, TypeKind.UINT):
                self.write("unsigned" if kind == TypeKind.UINT else "signed")
            elif kind == TypeKind.FLOAT:
                self.write("signed")
            elif kind == TypeKind.NONE:
                self.write("void")
            else:
                self.write("unsigned")
            if getattr(ty, "width", None) is not None:
                self.write("<")
                self.write(str(arch.get_const_or_val(ty.width)))
                self.write(">")
            return
        raise TypeError(f"Unsupported type object for CoreDSL2 writer: {type(ty)}")

    def write_attribute(self, attr, val=None):
        # print("attr", attr)
        if self.needsspace:
            self.write(" ")
        if val is not None:
            if isinstance(val, list) and len(val) == 0:
                val = None
        # if self.reduced and val is not None:
        #     return
        # TODO: allow atrbitrary attrs in cdsl2llvm parser, not only for operands
        if self.allowed_attrs is not None:
            allowed_attrs = [attr.lower() for attr in self.allowed_attrs]
            if self.reduced and attr.name.lower() not in allowed_attrs:
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
                if isinstance(val, str):  # TODO: replace with string literal
                    return val  # TODO: operation
                if isinstance(val, int):  # TODO: replace with int literal
                    return str(val)  # TODO: operation
                if isinstance(val, behav.Literal):
                    value = val.value
                    if val.ty.kind == TypeKind.STR:
                        if '"' not in value:
                            value = '"' + value + '"'
                    return str(value)
                if isinstance(val, behav.NamedReference):
                    return val.reference.name
                    # print("val", val)
                    # print("val.reference", val.reference)
                    # print("dir(val)", dir(val))
                    # return helper(arch.get_const_or_val(val))
                raise NotImplementedError(f"Unhandled case: {type(val)}")

            val = helper(val)
            self.write(val)
        self.write("]]")

    def write_operand(self, operand):
        self.write_type(operand.ty)
        self.write(" ")
        self.write(operand.name)
        self.write_attributes(operand.attributes)
        self.write_line(";")

    def write_assembly(self, instruction):
        # PatternGen's CDSL parser (ParseAssembly) supports the {"mnemonic", "args"}
        # tuple form regardless of reduced/compat mode; without it, it falls back to
        # guessing the mnemonic from the instruction name (assuming CORE-V naming),
        # which does not necessarily match the mnemonic declared in the CDSL source.
        self.write("assembly: ")
        mnemonic = instruction.mnemonic
        assembly = instruction.assembly
        if assembly is None:
            assembly = ""
        if mnemonic:
            self.write("{")
            self.write(f'"{mnemonic}"')
            self.write(", ")
        self.write(f'"{assembly}"')
        if mnemonic:
            self.write("}")
        self.write(";", nl=True)

    def write_constraints(self, constraints):
        for constraint in constraints:
            # print("constraint", constraint, type(constraint), dir(constraint))
            for stmt in constraint.stmts:
                visitor.generate(stmt, self)
                desc = constraint.description
                if desc:
                    self.write(f";  // {desc}", nl=True)
                else:
                    self.write(";", nl=True)

    def write_instruction_constraints(self, constraints, operands):
        if self.reduced:
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
        for _, op in enumerate(operands.values()):
            self.write_operand(op)
        # for i, op in enumerate(operands.values()):
        #     self.write_constraints(op.constraints)
        self.leave_block()

    def write_instruction(self, instruction):
        # print("write_instruction", instruction)
        self.write(instruction.name)
        self.write_attributes(instruction.attributes)
        self.enter_block()
        if self.is_seal5:
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
            if self.is_seal5:
                instruction._llvm_process_operands()
            self.write_instruction(instruction)
        self.leave_block()

    def write_set(self, set_def):
        # PatternGen's CDSL parser does not support the architectural_state section.
        if self.reduced:
            self.write("InstructionSet ")
            self.write(set_def.name)
            if set_def.extension:
                self.write(" extends ")
                self.write(", ".join(set_def.extension))
            self.enter_block()
            self.write_functions(set_def.functions)
            self.write_instructions(set_def.instructions)
            self.leave_block()
            return
        super().write_set(set_def)

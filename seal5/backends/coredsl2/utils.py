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

from seal5.logging import Logger

logger = Logger("backends.coredsl2_writer")


class Seal5CoreDSL2Writer(CoreDSL2Writer):

    def __init__(self, visitor, reduced: bool = True, skip_empty: bool = False, drop_first_op: bool = False, allowed_attrs: Optional[Set[str]] = None, version="coredsl2"):
        super().__init__(visitor, reduced=reduced, skip_empty=skip_empty, drop_first_op=drop_first_op, allowed_attrs=allowed_attrs)
        self.version = version
        self.level = 0

    @property
    def is_seal5(self):
        return self.version == "seal5"

    @property
    def is_coredsl2(self):
        return self.version == "coredsl2"


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

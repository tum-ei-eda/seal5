# SPDX-License-Identifier: Apache-2.0
#
# This file is part of the M2-ISA-R project: https://github.com/tum-ei-eda/M2-ISA-R
#
# Copyright (C) 2022
# Chair of Electrical Design Automation
# Technical University of Munich

"""TODO"""

from m2isar.metamodel import arch, behav
from seal5 import model

# pylint: disable=unused-argument


def operation(self: behav.Operation, context):
    statements = []
    for stmt in self.statements:
        temp = stmt.generate(context)
        if isinstance(temp, list):
            statements.extend(temp)
        else:
            statements.append(temp)

    self.statements = statements
    return self


def binary_operation(self: behav.BinaryOperation, context):
    self.left = self.left.generate(context)
    self.right = self.right.generate(context)

    return self


def slice_operation(self: behav.SliceOperation, context):
    self.expr = self.expr.generate(context)
    self.left = self.left.generate(context)
    self.right = self.right.generate(context)

    return self


def concat_operation(self: behav.ConcatOperation, context):
    self.left = self.left.generate(context)
    self.right = self.right.generate(context)

    return self


def number_literal(self: behav.IntLiteral, context):
    return self


def int_literal(self: behav.IntLiteral, context):
    return self


def scalar_definition(self: behav.ScalarDefinition, context):
    return self


def break_(self: behav.Break, context):
    return self


def assignment(self: behav.Assignment, context):
    self.target = self.target.generate(context)
    self.expr = self.expr.generate(context)

    return self


def conditional(self: behav.Conditional, context):
    # print("conditional")
    self.conds = [x.generate(context) for x in self.conds]
    self.stmts = [x.generate(context) for x in self.stmts]

    return self


def loop(self: behav.Loop, context):
    self.cond = self.cond.generate(context)
    self.stmts = [x.generate(context) for x in self.stmts]

    return self


def ternary(self: behav.Ternary, context):
    self.cond = self.cond.generate(context)
    self.then_expr = self.then_expr.generate(context)
    self.else_expr = self.else_expr.generate(context)

    return self


def return_(self: behav.Return, context):
    if self.expr is not None:
        self.expr = self.expr.generate(context)

    return self


def unary_operation(self: behav.UnaryOperation, context):
    self.right = self.right.generate(context)

    return self


def named_reference(self: behav.NamedReference, context):
    # if isinstance(self.reference, arch.BitFieldDescr):
    # raise NotImplementedError
    return self


def indexed_reference(self: behav.IndexedReference, context):
    print("indexed_reference", self)
    print("self.reference", self.reference)
    print("self.index", self.index)
    if isinstance(self.reference, arch.Memory):
        mem_name = self.reference.name
        mem = self.reference
        mem_size = mem.size
        mem_lanes = 1
        index = self.index
        offset = 0
        if isinstance(index, behav.BinaryOperation):  # offset?
            print("binop!")
            if index.op.value == "+":
                print("offset!")
                if isinstance(index.left, behav.NamedReference):
                    print("lhs named")
                    if isinstance(index.right, behav.IntLiteral):
                        print("rhs const")
                        offset = index.right.value
                        index = index.left
                elif isinstance(index.right, behav.NamedReference):
                    print("rhs named")
                    if isinstance(index.left, behav.IntLiteral):
                        print("lhs const")
                        offset = index.left.value
                        index = index.right
        print("index", index)
        print("offset", offset)
        if isinstance(index, behav.NamedReference):
            if isinstance(index.reference, arch.BitFieldDescr):
                op_name = index.reference.name
                assert op_name in context.operands
                op = context.operands[op_name]
                if mem_name == "X":
                    if offset == 0:
                        reg_class = model.Seal5RegisterClass.GPR
                    elif offset == 8:
                        reg_class = model.Seal5RegisterClass.GPRC
                    else:
                        raise NotImplementedError(f"GPR with offset {offset}")
                elif mem_name == "F":
                    assert offset == 0
                    reg_class = model.Seal5RegisterClass.FPR
                elif mem_name == "CSR":
                    assert offset == 0
                    reg_class = model.Seal5RegisterClass.CSR
                else:
                    assert offset == 0  # TODO: write offset to Operand class?
                    reg_class = model.Seal5RegisterClass.UNKNOWN
                if not isinstance(op, model.Seal5RegOperand):
                    op = model.Seal5RegOperand(op.name, op.ty, op.attributes, op.constraints, reg_class=reg_class)
                reg_ty = model.Seal5Type(arch.DataType.U, mem_size, mem_lanes)
                op.reg_ty = reg_ty
                context.operands[op_name] = op
    # input("1111")
    self.index = self.index.generate(context)

    return self


def type_conv(self: behav.TypeConv, context):
    self.expr = self.expr.generate(context)

    return self


def callable_(self: behav.Callable, context):
    self.args = [stmt.generate(context) for stmt in self.args]

    return self


def group(self: behav.Group, context):
    self.expr = self.expr.generate(context)

    return self


def procedure_call(self: behav.ProcedureCall, context):
    self.fn_args = [arg.generate(context) for arg in self.args]
    return self

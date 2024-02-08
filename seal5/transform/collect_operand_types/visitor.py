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
    self.index = self.index.generate(context)

    return self


def type_conv(self: behav.TypeConv, context):
    # print("type_conv", self, dir(self))
    self.expr = self.expr.generate(context)
    if isinstance(self.expr, behav.NamedReference):  # imm?
        if isinstance(self.expr.reference, arch.BitFieldDescr):
            name = self.expr.reference.name
            assert name in context.operands
            op = context.operands[name]
            assert isinstance(op, model.Seal5ImmOperand)
            ty = op.ty
            width = ty.width
            if ty != self.data_type:
                # update
                if ty.datatype == arch.DataType.U:
                    ty.datatype = self.data_type
                    op.ty = ty

                else:
                    assert False, "Conflicting types"
            if self.size is not None:
                if width != self.size:
                    if self.size < width:  # trunc!
                        assert False, "truncation not allowed here"
                    elif self.size > width:  # zext/sext!
                        assert False, "sign/zero extension not allowed here"
            # print("op", name, op, type(op))
            # if not isinstance(op, model.Seal5ImmOperand):
            # op = model.Seal5ImmOperand(op.name, op.ty, op.attributes, op.constraints)
            context.operands[name] = op
            # if self.data_type != arch.DataType.U:  # Default to unsigned
            # if self.size is not None:
            #     # Do not allow truncation
            #     assert self.size == self.expr.reference.size
            # else:
            #     # add explicit size (optional?)
            #     self.size = self.expr.reference.size
            # if self.data_type:
            #     if self.data_type != self.reference.data_type:
            #         # Do not update BitFieldDescr for now...
            #         # self.expr.reference.data_type = self.data_type
    elif isinstance(self.expr, behav.IndexedReference):  # X[reg]?
        if isinstance(self.expr.reference, arch.Memory):
            if isinstance(self.expr.index, behav.NamedReference):
                if isinstance(self.expr.index.reference, arch.BitFieldDescr):
                    op_name = self.expr.index.reference.name
                    assert op_name in context.operands
                    op = context.operands[op_name]
                    assert isinstance(op, model.Seal5RegOperand)
                    reg_ty = op.reg_ty
                    width = reg_ty.width
                    # print("op", op, op.name, op.reg_class, op.reg_ty, op.ty, op.attributes, op.constraints)
                    if reg_ty != self.data_type:
                        # update
                        if reg_ty.datatype == arch.DataType.U:
                            reg_ty.datatype = self.data_type
                            op.reg_ty = reg_ty

                        else:
                            assert False, "Conflicting types"
                    if self.size is not None:
                        if width != self.size:
                            if self.size < width:  # trunc!
                                return self
                                # assert False, "truncation not allowed here"
                            elif self.size > width:  # zext/sext!
                                assert False, "sign/zero extension not allowed here"
                    context.operands[op_name] = op

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

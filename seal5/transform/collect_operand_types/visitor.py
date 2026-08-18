# SPDX-License-Identifier: Apache-2.0
#
# This file is part of the M2-ISA-R project: https://github.com/tum-ei-eda/M2-ISA-R
#
# Copyright (C) 2022
# Chair of Electrical Design Automation
# Technical University of Munich

"""Collect operand types from behavior expressions."""

from functools import singledispatchmethod

from m2isar.metamodel import arch, behav
from m2isar.metamodel.utils.ExprVisitor import ExprVisitor
from seal5 import model

# pylint: disable=unused-argument


class CollectOperandTypesVisitor(ExprVisitor):
    """Collect operand types from behavioral expressions."""

    @singledispatchmethod
    def generate(self, expr: behav.BaseNode, context):
        raise NotImplementedError(
            f"No visit method implemented for type "
            f"{type(expr).__name__} in {type(self).__name__}"
        )

    @generate.register
    def _(self, expr: behav.Operation, context):
        statements = []
        for stmt in expr.statements:
            temp = self.generate(stmt, context)
            if isinstance(temp, list):
                statements.extend(temp)
            else:
                statements.append(temp)

        expr.statements = statements
        return expr

    @generate.register
    def _(self, expr: behav.BinaryOperation, context):
        expr.left = self.generate(expr.left, context)
        expr.right = self.generate(expr.right, context)

        return expr

    @generate.register
    def _(self, expr: behav.SliceOperation, context):
        expr.expr = self.generate(expr.expr, context)
        expr.left = self.generate(expr.left, context)
        expr.right = self.generate(expr.right, context)

        return expr

    @generate.register
    def _(self, expr: behav.ConcatOperation, context):
        expr.left = self.generate(expr.left, context)
        expr.right = self.generate(expr.right, context)

        return expr

    @generate.register
    def _(self, expr: behav.Literal, context):
        return expr

    @generate.register
    def _(self, expr: behav.Tensor, context):
        return expr

    @generate.register
    def _(self, expr: behav.VarDefinition, context):
        return expr

    @generate.register
    def _(self, expr: behav.Break, context):
        return expr

    @generate.register
    def _(self, expr: behav.Assignment, context):
        expr.target = self.generate(expr.target, context)
        expr.expr = self.generate(expr.expr, context)

        return expr

    @generate.register
    def _(self, expr: behav.Conditional, context):
        # print("conditional")
        expr.conds = [self.generate(x, context) for x in expr.conds]
        expr.stmts = [self.generate(x, context) for x in expr.stmts]

        return expr

    @generate.register
    def _(self, expr: behav.Loop, context):
        expr.cond = self.generate(expr.cond, context)
        expr.stmts = [self.generate(x, context) for x in expr.stmts]

        return expr

    @generate.register
    def _(self, expr: behav.Ternary, context):
        expr.cond = self.generate(expr.cond, context)
        expr.then_expr = self.generate(expr.then_expr, context)
        expr.else_expr = self.generate(expr.else_expr, context)

        return expr

    @generate.register
    def _(self, expr: behav.Return, context):
        if expr.expr is not None:
            expr.expr = self.generate(expr.expr, context)

        return expr

    @generate.register
    def _(self, expr: behav.UnaryOperation, context):
        expr.right = self.generate(expr.right, context)

        return expr

    @generate.register
    def _(self, expr: behav.NamedReference, context):
        # if isinstance(expr.reference, arch.BitFieldDescr):
        # raise NotImplementedError
        return expr

    @generate.register
    def _(self, expr: behav.IndexedReference, context):
        expr.index = self.generate(expr.index, context)

        return expr

    @generate.register
    def _(self, expr: behav.TypeConv, context):
        # print("type_conv", expr, dir(expr))
        expr.expr = self.generate(expr.expr, context)
        if isinstance(expr.expr, behav.NamedReference):  # imm?
            if isinstance(expr.expr.reference, arch.BitFieldDescr):
                name = expr.expr.reference.name
                assert name in context.operands
                op = context.operands[name]
                assert isinstance(op, model.Seal5ImmOperand)
                ty = op.ty
                width = ty.size  # Changed from .width to .size
                if ty != expr.data_type:
                    # update
                    if ty.kind == 'U':  # Changed from datatype to kind
                        ty.kind = expr.data_type
                        op.ty = ty

                    else:
                        assert False, "Conflicting types"
                if expr.size is not None:
                    if width != expr.size:
                        if expr.size < width:  # trunc!
                            assert False, "truncation not allowed here"
                        elif expr.size > width:  # zext/sext!
                            assert False, "sign/zero extension not allowed here"
                # print("op", name, op, type(op))
                # if not isinstance(op, model.Seal5ImmOperand):
                # op = model.Seal5ImmOperand(op.name, op.ty, op.attributes, op.constraints)
                context.operands[name] = op
                # if expr.data_type != arch.DataType.U:  # Default to unsigned
                # if expr.size is not None:
                #     # Do not allow truncation
                #     assert expr.size == expr.expr.reference.size
                # else:
                #     # add explicit size (optional?)
                #     expr.size = expr.expr.reference.size
                # if expr.data_type:
                #     if expr.data_type != expr.reference.data_type:
                #         # Do not update BitFieldDescr for now...
                #         # expr.expr.reference.data_type = expr.data_type
        elif isinstance(expr.expr, behav.IndexedReference):  # X[reg]?
            if isinstance(expr.expr.reference, (arch.Memory, arch.RegisterBank)):
                if isinstance(expr.expr.index, behav.NamedReference):
                    if isinstance(expr.expr.index.reference, arch.BitFieldDescr):
                        op_name = expr.expr.index.reference.name
                        assert op_name in context.operands
                        op = context.operands[op_name]
                        assert isinstance(op, model.Seal5RegOperand)
                        reg_ty = op.reg_ty
                        width = reg_ty.size  # Changed from .width to .size
                        # print("op", op, op.name, op.reg_class, op.reg_ty, op.ty, op.attributes, op.constraints)
                        if reg_ty != expr.data_type:
                            # update
                            if reg_ty.kind == 'U':  # Changed from datatype to kind
                                reg_ty.kind = expr.data_type
                                op.reg_ty = reg_ty

                            else:
                                assert False, "Conflicting types"
                        if expr.size is not None:
                            if width != expr.size:
                                if expr.size < width:  # trunc!
                                    return expr
                                    # assert False, "truncation not allowed here"
                                if expr.size > width:  # zext/sext!
                                    assert False, "sign/zero extension not allowed here"
                        context.operands[op_name] = op

        return expr

    @generate.register
    def _(self, expr: behav.Callable, context):
        expr.args = [self.generate(arg, context) for arg in expr.args]

        return expr

    @generate.register
    def _(self, expr: behav.Group, context):
        expr.expr = self.generate(expr.expr, context)

        return expr

    @generate.register
    def _(self, expr: behav.ProcedureCall, context):
        expr.fn_args = [self.generate(arg, context) for arg in expr.args]
        return expr

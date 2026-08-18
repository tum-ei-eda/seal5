# SPDX-License-Identifier: Apache-2.0
#
# This file is part of the M2-ISA-R project: https://github.com/tum-ei-eda/M2-ISA-R
#
# Copyright (C) 2022
# Chair of Electrical Design Automation
# Technical University of Munich

"""Collect register operands from behavior expressions."""

from functools import singledispatchmethod

from m2isar.metamodel import arch, behav
from m2isar.metamodel.utils.ExprVisitor import ExprVisitor
from seal5 import model

# pylint: disable=unused-argument


class CollectRegisterOperandsVisitor(ExprVisitor):
    """Collect register operands from behavioral expressions."""

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
        # print("indexed_reference", self)
        # print("expr.reference", expr.reference)
        # print("expr.index", expr.index)
        if isinstance(expr.reference, arch.Memory):
            mem_name = expr.reference.name
            mem = expr.reference
            mem_size = mem.size
            mem_lanes = 1
            index = expr.index
            offset = 0
            if isinstance(index, behav.BinaryOperation):  # offset?
                # print("binop!")
                if index.op.value == "+":
                    # print("offset!")
                    if isinstance(index.left, behav.NamedReference):
                        # print("lhs named")
                        if isinstance(index.right, behav.Literal):
                            # print("rhs const")
                            offset = index.right.value
                            index = index.left
                    elif isinstance(index.right, behav.NamedReference):
                        # print("rhs named")
                        if isinstance(index.left, behav.Literal):
                            # print("lhs const")
                            offset = index.left.value
                            index = index.right
            # print("index", index)
            # print("offset", offset)
            if isinstance(index, behav.NamedReference):
                if isinstance(index.reference, arch.BitFieldDescr):
                    op_name = index.reference.name
                    assert op_name in context.operands
                    op = context.operands[op_name]
                    reg_ty_ = arch.DataType.U
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
                        assert mem_size in [32, 64]
                        reg_ty_ = arch.DataType.F if mem_size == 32 else arch.DataType.F
                    elif mem_name == "CSR":
                        assert offset == 0
                        reg_class = model.Seal5RegisterClass.CSR
                    else:
                        assert offset == 0  # TODO: write offset to Operand class?
                        reg_class = model.Seal5RegisterClass.UNKNOWN
                    if not isinstance(op, model.Seal5RegOperand):
                        op = model.Seal5RegOperand(op.name, op.ty, op.attributes, op.constraints, reg_class=reg_class)
                    reg_ty = model.Seal5Type(reg_ty_, mem_size, mem_lanes)
                    op.reg_ty = reg_ty
                    context.operands[op_name] = op
        # input("1111")
        expr.index = self.generate(expr.index, context)

        return expr

    @generate.register
    def _(self, expr: behav.TypeConv, context):
        expr.expr = self.generate(expr.expr, context)

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

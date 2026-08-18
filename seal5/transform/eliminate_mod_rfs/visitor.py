# SPDX-License-Identifier: Apache-2.0
#
# This file is part of the M2-ISA-R project: https://github.com/tum-ei-eda/M2-ISA-R
#
# Copyright (C) 2022
# Chair of Electrical Design Automation
# Technical University of Munich

"""Eliminate modulo RFS operations from behavioral expressions."""

from functools import singledispatchmethod

from m2isar.metamodel import behav
from m2isar.metamodel.utils.ExprVisitor import ExprVisitor

# pylint: disable=unused-argument

RFS = 32  # TODO: do not hardcode


class EliminateModRfsVisitor(ExprVisitor):
    """Eliminate (rd != 0) modulo RFS checks from behavioral expressions."""

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
        # TODO: figure out rfs from symbols!
        # TODO: support swapped operand order
        if expr.op.value == "%":
            lhs = expr.left
            while isinstance(lhs, behav.Group):
                lhs = lhs.expr
            expr.left = lhs
            if isinstance(expr.left, behav.NamedReference):
                if isinstance(expr.right, behav.Literal):
                    if expr.right.value == RFS:
                        expr.left = self.generate(expr.left, context)
                        return expr.left

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
        expr.conds = [self.generate(x, context) for x in expr.conds]

        # Keep the same legacy handling as InferTypesMutator.
        stmts = []
        for stmt in expr.stmts:
            if isinstance(stmt, list):
                new = [self.generate(x, context) for x in stmt]
            else:
                new = self.generate(stmt, context)
            stmts.append(new)

        expr.stmts = stmts
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
        return expr

    @generate.register
    def _(self, expr: behav.IndexedReference, context):
        expr.index = self.generate(expr.index, context)

        # New IndexedReference supports ranged accesses.
        if expr.right is not None:
            expr.right = self.generate(expr.right, context)

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
        return expr

# SPDX-License-Identifier: Apache-2.0
#
# This file is part of the M2-ISA-R project: https://github.com/tum-ei-eda/M2-ISA-R
#
# Copyright (C) 2022
# Chair of Electrical Design Automation
# Technical University of Munich

"""A transformation module for making implicit truncations explicit in M2-ISA-R behavior expressions."""

from functools import singledispatchmethod

from m2isar.metamodel import behav, type_info
from m2isar.metamodel.utils.ExprVisitor import ExprVisitor

from seal5.logging import Logger

logger = Logger("transform.explicit_truncations")

# pylint: disable=unused-argument


class ExplicitTruncationsVisitor(ExprVisitor):
    """Make implicit truncations explicit in behavioral expressions."""

    @singledispatchmethod
    def generate(self, expr: behav.BaseNode, context):
        raise NotImplementedError(
            f"No visit method implemented for type " f"{type(expr).__name__} in {type(self).__name__}"
        )

    @generate.register
    def _(self, expr: behav.Operation, context):
        statements = []
        for stmt in expr.statements:
            try:
                temp = self.generate(stmt, context)
                if isinstance(temp, list):
                    statements.extend(temp)
                else:
                    statements.append(temp)
            except (NotImplementedError, ValueError):
                logger.debug(f"cant simplify {stmt}")

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
        if expr.target.ty and expr.expr.ty:
            if isinstance(expr.target.ty, type_info.ArrayType):
                raise NotImplementedError("ArrayType")
            target_width = expr.target.ty.size
            expr_width = expr.expr.ty.size
            if target_width < expr_width:  # implicit truncation
                ty = expr.expr.ty
                ty_copy = type(ty)(size=target_width, kind=ty.kind if hasattr(ty, "kind") else "U")
                group_ = behav.Group(expr.expr)
                group_.ty = ty_copy
                expr.expr = behav.SliceOperation(group_, behav.Literal(target_width - 1), behav.Literal(0))
                expr.expr.ty = ty_copy

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

        if isinstance(expr.expr, behav.Literal):
            return expr.expr

        return expr

    @generate.register
    def _(self, expr: behav.ProcedureCall, context):
        return expr

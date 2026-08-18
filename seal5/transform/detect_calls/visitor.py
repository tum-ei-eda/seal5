# SPDX-License-Identifier: Apache-2.0
#
# This file is part of the M2-ISA-R project: https://github.com/tum-ei-eda/M2-ISA-R
#
# Copyright (C) 2022
# Chair of Electrical Design Automation
# Technical University of Munich

"""Identify instructions with procedure calls."""

from functools import singledispatchmethod

from m2isar.metamodel import arch, behav
from m2isar.metamodel.utils.ExprVisitor import ExprVisitor

# pylint: disable=unused-argument


class DetectCallsVisitor(ExprVisitor):
    """Detect whether a behavioral expression contains a procedure call."""

    @singledispatchmethod
    def generate(self, expr: behav.BaseNode, context):
        raise NotImplementedError(
            f"No visit method implemented for type {type(expr).__name__} in {type(self).__name__}"
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
    def _(self, expr: behav.Block, context):
        stmts = []
        for stmt in expr.statements:
            stmt = self.generate(stmt, context)
            if isinstance(stmt, behav.Conditional):
                if len(stmt.conds) == 1 and isinstance(stmt.stmts[0], behav.Block) and len(stmt.stmts[0].statements) == 0:
                    continue
            stmts.append(stmt)
        expr.statements = stmts
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
        expr.conds = [self.generate(cond, context) for cond in expr.conds]
        for op in expr.stmts:
            op.generate(context)
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
        if isinstance(expr.reference, (arch.Memory, arch.RegisterBank)):
            expr.index = self.generate(expr.index, context)
        return expr

    @generate.register
    def _(self, expr: behav.TypeConv, context):
        expr.expr = self.generate(expr.expr, context)
        return expr

    @generate.register
    def _(self, expr: behav.Callable, context):
        context.has_call = True
        expr.args = [self.generate(stmt, context) for stmt in expr.args]
        return expr

    @generate.register
    def _(self, expr: behav.Group, context):
        expr.expr = self.generate(expr.expr, context)
        return expr

    @generate.register
    def _(self, expr: behav.ProcedureCall, context):
        context.has_call = True
        expr.fn_args = [self.generate(arg, context) for arg in expr.args]
        return expr

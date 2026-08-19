# SPDX-License-Identifier: Apache-2.0
#
# This file is part of the M2-ISA-R project: https://github.com/tum-ei-eda/M2-ISA-R
#
# Copyright (C) 2022
# Chair of Electrical Design Automation
# Technical University of Munich

"""A transformation module for simplifying M2-ISA-R behavior expressions. The following
simplifications are done:

* Resolvable :class:`m2isar.metamodel.arch.Constant` s are replaced by
  `m2isar.metamodel.behav.Literal` s representing their value
* Fully resolvable arithmetic operations are carried out and their results
  represented as a matching :class:`m2isar.metamodel.behav.Literal`
* Conditions and loops with fully resolvable conditions are either discarded entirely
  or transformed into code blocks without any conditions
* Ternaries with fully resolvable conditions are transformed into only the matching part
* Type conversions of :class:`m2isar.metamodel.behav.Literal` s apply the desired
  type directly to the :class:`Literal` and discard the type conversion
"""

from functools import singledispatchmethod

from m2isar.metamodel import behav, type_info
from m2isar.metamodel.utils.ExprVisitor import ExprVisitor

from seal5.logging import Logger

logger = Logger("transform.simplify_trivial_slices")

# pylint: disable=unused-argument


class SimplifyTrivialSlicesVisitor(ExprVisitor):
    """Simplify trivial slice operations in behavioral expressions."""

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

        if expr.expr.ty is None:
            logger.warning("Slice Operation needs inferred type. Skipping...")
            return expr

        # Check if the type is a PrimitiveType (new system)
        if not isinstance(expr.expr.ty, type_info.PrimitiveType):
            logger.warning("Slice Operation needs PrimitiveType. Skipping...")
            return expr

        source_width = expr.expr.ty.width

        expr.left = self.generate(expr.left, context)
        if not isinstance(expr.left, behav.Literal):
            return expr

        expr.right = self.generate(expr.right, context)
        if not isinstance(expr.right, behav.Literal):
            return expr

        assert expr.left.value >= expr.right.value
        target_width = expr.left.value - expr.right.value + 1
        assert target_width <= source_width

        if source_width == target_width:
            return behav.Group(expr.expr)

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


def named_reference(self: behav.NamedReference, context):
    return self


def indexed_reference(self: behav.IndexedReference, context):
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

    if isinstance(self.expr, behav.IntLiteral):
        return self.expr

    return self


def break_(self: behav.Break, context):
    return self

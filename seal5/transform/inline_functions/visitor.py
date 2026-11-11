# SPDX-License-Identifier: Apache-2.0
#
# This file is part of the M2-ISA-R project: https://github.com/tum-ei-eda/M2-ISA-R
#
# Copyright (C) 2024
# Chair of Electrical Design Automation
# Technical University of Munich

"""Inline functions within instructions in the M2-ISA-R metamodel."""

from copy import deepcopy
from functools import singledispatchmethod

from m2isar.metamodel import behav
from m2isar.metamodel.utils.ExprVisitor import ExprVisitor

from seal5.model import Seal5FunctionAttribute

# pylint: disable=unused-argument


class ReplaceContext:
    def __init__(self, mapping):
        self.mapping = mapping


class InlineFunctionsVisitor(ExprVisitor):
    """Inline function calls within behavioral expressions."""

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
                print(f"cant simplify {stmt}")

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
        # print("named_refernce", self, dir(self))
        if isinstance(context, ReplaceContext):
            matched = context.mapping.get(expr.reference.name, None)
            if matched is not None:
                return deepcopy(matched)
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
        # print("type_conv", self)
        expr.expr = self.generate(expr.expr, context)

        return expr

    @generate.register
    def _(self, expr: behav.Callable, context):
        # Substitute call arguments first; function lookup belongs to the outer context.
        expr.args = [self.generate(arg, context) for arg in expr.args]
        if isinstance(context, ReplaceContext):
            return expr
        function_def = (
            context.functions.get(expr.ref_or_name) if isinstance(expr.ref_or_name, str) else expr.ref_or_name
        )
        if function_def is None or function_def.extern:
            return expr
        if Seal5FunctionAttribute.INLINE not in function_def.attributes:
            return expr
        if len(function_def.operation.statements) != 1:
            return expr
        statement = function_def.operation.statements[0]
        while isinstance(statement, behav.Block):
            if len(statement.statements) != 1:
                return expr
            statement = statement.statements[0]
        if not isinstance(statement, behav.Return) or statement.expr is None:
            return expr
        if len(function_def.args) != len(expr.args):
            return expr
        active = getattr(context, "active_functions", set())
        if function_def.name in active:
            return expr
        context.active_functions = active
        active.add(function_def.name)
        try:
            # Each call needs its own tree; never rewrite the shared function body.
            ret_expr = deepcopy(statement.expr)
            mapping = {
                name: behav.TypeConv(param.ty.kind, param.ty.size, deepcopy(arg))
                for (name, param), arg in zip(function_def.args.items(), expr.args)
            }
            ret_expr = self.generate(ret_expr, ReplaceContext(mapping))
            ret_expr = self.generate(ret_expr, context)
            # Convert the value after unwrapping Return, preserving function return width.
            return behav.TypeConv(function_def.ty.kind, function_def.ty.size, ret_expr)
        finally:
            active.remove(function_def.name)

    @generate.register
    def _(self, expr: behav.Group, context):
        expr.expr = self.generate(expr.expr, context)

        return expr

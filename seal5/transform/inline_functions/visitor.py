# SPDX-License-Identifier: Apache-2.0
#
# This file is part of the M2-ISA-R project: https://github.com/tum-ei-eda/M2-ISA-R
#
# Copyright (C) 2024
# Chair of Electrical Design Automation
# Technical University of Munich

"""Inline functions within instructions in the M2-ISA-R metamodel."""

from functools import singledispatchmethod

from m2isar.metamodel import arch, behav
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
                return matched
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
        # print("callable_", self, dir(self))
        # print("self.ref_or_name", self.ref_or_name)
        # print("context.functions", context.functions)
        if isinstance(expr.ref_or_name, str):
            function_def = context.functions.get(expr.ref_or_name)
        else:
            assert isinstance(expr.ref_or_name, arch.Function)
            function_def = expr.ref_or_name
        # Retrieve the function definition
        # print("function_def", function_def)
        # print("function_def.attributes", function_def.attributes)
        if Seal5FunctionAttribute.INLINE not in function_def.attributes:
            return expr

        # Check if the function is external or has early returns that prevent inlining
        if function_def is None or function_def.extern:
            return expr  # Cannot inline an external or undefined function

        if len(function_def.operation.statements) != 1:
            return expr

        statement = function_def.operation.statements[0]
        ret_dtype = function_def.data_type
        ret_size = None  # TODO: add sized return types to m2isar functions
        statement = behav.TypeConv(ret_dtype, ret_size, statement)
        # print("statement", statement)
        while isinstance(statement, behav.Block):
            # print("BLOCK", statement, dir(statement))
            statements = statement.statements
            if len(statements) != 1:
                return expr
            statement = statements[0]
        # print("statement", statement, dir(statement))
        # print("?", [isinstance(stmt, behav.Return) for stmt in function_def.operation.statements])
        if not isinstance(statement, behav.Return):
            return expr
        # return self  # Skip inlining if the function has a return statement
        # Map the arguments of the function to the corresponding expressions
        arg_map = {param_name: arg for param_name, arg in zip(function_def.args, expr.args)}
        # print("arg_map", arg_map)
        ret_expr = statement.expr
        # print("ret_expr", ret_expr)
        replace_context = ReplaceContext(mapping=arg_map)
        ret_expr.generate(replace_context)
        ret_expr.generate(context)
        return ret_expr

    @generate.register
    def _(self, expr: behav.Group, context):
        expr.expr = self.generate(expr.expr, context)

        return expr

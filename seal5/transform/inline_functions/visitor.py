# SPDX-License-Identifier: Apache-2.0
#
# This file is part of the M2-ISA-R project: https://github.com/tum-ei-eda/M2-ISA-R
#
# Copyright (C) 2024
# Chair of Electrical Design Automation
# Technical University of Munich

"""This module inlines functions within instructions in the M2-ISA-R metamodel."""

from m2isar.metamodel import arch, behav


from seal5.model import Seal5FunctionAttribute

# pylint: disable=unused-argument


class ReplaceContext:
    def __init__(self, mapping):
        self.mapping = mapping


def operation(self: behav.Operation, context):
    statements = []
    for stmt in self.statements:
        try:
            temp = stmt.generate(context)
            if isinstance(temp, list):
                statements.extend(temp)
            else:
                statements.append(temp)
        except (NotImplementedError, ValueError):
            print(f"cant simplify {stmt}")

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
    # print("named_refernce", self, dir(self))
    if isinstance(context, ReplaceContext):
        matched = context.mapping.get(self.reference.name, None)
        if matched is not None:
            return matched
    return self


def indexed_reference(self: behav.IndexedReference, context):
    self.index = self.index.generate(context)

    return self


def type_conv(self: behav.TypeConv, context):
    # print("type_conv", self)
    self.expr = self.expr.generate(context)

    return self


def callable_(self: behav.Callable, context):
    # print("callable_", self, dir(self))
    # print("self.ref_or_name", self.ref_or_name)
    # print("context.functions", context.functions)
    if isinstance(self.ref_or_name, str):
        function_def = context.functions.get(self.ref_or_name)
    else:
        assert isinstance(self.ref_or_name, arch.Function)
        function_def = self.ref_or_name
    # Retrieve the function definition
    # print("function_def", function_def)
    # print("function_def.attributes", function_def.attributes)
    if Seal5FunctionAttribute.INLINE not in function_def.attributes:
        return self

    # Check if the function is external or has early returns that prevent inlining
    if function_def is None or function_def.extern:
        return self  # Cannot inline an external or undefined function

    if len(function_def.operation.statements) != 1:
        return self

    statement = function_def.operation.statements[0]
    ret_dtype = function_def.data_type
    ret_size = None  # TODO: add sized return types to m2isar functions
    statement = behav.TypeConv(ret_dtype, ret_size, statement)
    # print("statement", statement)
    while isinstance(statement, behav.Block):
        # print("BLOCK", statement, dir(statement))
        statements = statement.statements
        if len(statements) != 1:
            return self
        statement = statements[0]
    # print("statement", statement, dir(statement))
    # print("?", [isinstance(stmt, behav.Return) for stmt in function_def.operation.statements])
    if not isinstance(statement, behav.Return):
        return self
    # return self  # Skip inlining if the function has a return statement
    # Map the arguments of the function to the corresponding expressions
    arg_map = {param_name: arg for param_name, arg in zip(function_def.args, self.args)}
    # print("arg_map", arg_map)
    ret_expr = statement.expr
    # print("ret_expr", ret_expr)
    replace_context = ReplaceContext(mapping=arg_map)
    ret_expr.generate(replace_context)
    ret_expr.generate(context)
    return ret_expr

    return self


def group(self: behav.Group, context):
    self.expr = self.expr.generate(context)

    return self

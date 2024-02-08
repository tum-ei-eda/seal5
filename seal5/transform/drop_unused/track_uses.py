# SPDX-License-Identifier: Apache-2.0
#
# This file is part of the M2-ISA-R project: https://github.com/tum-ei-eda/M2-ISA-R
#
# Copyright (C) 2022
# Chair of Electrical Design Automation
# Technical University of Munich

"""TODO"""

from m2isar.metamodel import arch, behav

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
    # print("named_reference", self.reference.name)
    if isinstance(self.reference, (arch.Constant, arch.Memory, arch.Scalar)):
        context.track(self.reference.name)
    # if isinstance(self.reference, arch.Constant):
    # 	return behav.IntLiteral(self.reference.value, self.reference.size, self.reference.signed)

    # if isinstance(self.reference, arch.Scalar) and self.reference.value is not None:
    # 		return behav.IntLiteral(self.reference.value, self.reference.size, self.reference.data_type == arch.DataType.S)

    return self


def indexed_reference(self: behav.IndexedReference, context):
    # print("indexed_reference", self.reference.name)
    if isinstance(self.reference, arch.Memory):
        context.track(self.reference.name)
    self.index = self.index.generate(context)

    return self


def type_conv(self: behav.TypeConv, context):
    self.expr = self.expr.generate(context)

    return self


def callable_(self: behav.Callable, context):
    if isinstance(self.ref_or_name, str):
        name = self.ref_or_name
    else:
        name = self.ref_or_name.name
    context.track(name)
    self.args = [stmt.generate(context) for stmt in self.args]

    return self


def group(self: behav.Group, context):
    self.expr = self.expr.generate(context)

    return self

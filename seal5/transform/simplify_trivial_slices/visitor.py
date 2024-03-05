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
  `m2isar.metamodel.arch.IntLiteral` s representing their value
* Fully resolvable arithmetic operations are carried out and their results
  represented as a matching :class:`m2isar.metamodel.arch.IntLiteral`
* Conditions and loops with fully resolvable conditions are either discarded entirely
  or transformed into code blocks without any conditions
* Ternaries with fully resolvable conditions are transformed into only the matching part
* Type conversions of :class:`m2isar.metamodel.arch.IntLiteral` s apply the desired
  type directly to the :class:`IntLiteral` and discard the type conversion
"""
import logging
from m2isar.metamodel import arch, behav

logger = logging.getLogger(__name__)


# pylint: disable=unused-argument


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
    # print("slice_operation")
    self.expr = self.expr.generate(context)

    if self.expr.inferred_type is None:
        logger.warning("Slice Operation needs inferred type. Skipping...")
        return self
    assert isinstance(self.expr.inferred_type, arch.IntegerType)
    source_width = self.expr.inferred_type.width
    # print("source_width", source_width)
    self.left = self.left.generate(context)
    if not isinstance(self.left, behav.IntLiteral):
        return self
    self.right = self.right.generate(context)
    if not isinstance(self.right, behav.IntLiteral):
        return self
    assert self.left.value >= self.right.value
    target_width = self.left.value - self.right.value + 1
    # print("target_width", target_width)
    assert target_width <= source_width

    # input("@")
    if source_width == target_width:
        return behav.Group(self.expr)

    # if self.right.value == 0:
    #     return behav.TypeConv(arch.DataType.S if self.expr.inferred_type.signed
    #        else arch.DataType.U, target_width, self.expr)
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


def assignment(self: behav.Assignment, context):
    self.target = self.target.generate(context)
    self.expr = self.expr.generate(context)

    # if isinstance(self.expr, behav.IntLiteral) and isinstance(self.target, behav.ScalarDefinition):
    #       self.target.scalar.value = self.expr.value

    return self


def conditional(self: behav.Conditional, context):
    self.conds = [x.generate(context) for x in self.conds]
    # self.stmts = [[y.generate(context) for y in x] for x in self.stmts]
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

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
from m2isar.metamodel import behav

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


def assignment(self: behav.Assignment, context):
    if self.target.inferred_type and self.expr.inferred_type:
        target_width = self.target.inferred_type.width
        expr_width = self.expr.inferred_type.width
        # print("tw", target_width)
        # print("ew", expr_width)
        # input("123")
        if target_width < expr_width:  # implicit truncation
            ty = self.expr.inferred_type
            ty._width = target_width
            group = behav.Group(self.expr)
            group.inferred_type = ty
            self.expr = behav.SliceOperation(group, behav.IntLiteral(target_width - 1), behav.IntLiteral(0))
            self.expr.inferred_type = ty
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

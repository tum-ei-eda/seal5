# SPDX-License-Identifier: Apache-2.0
#
# This file is part of the M2-ISA-R project: https://github.com/tum-ei-eda/M2-ISA-R
#
# Copyright (C) 2022
# Chair of Electrical Design Automation
# Technical University of Munich

"""Detect immediate-value leaves within instruction behavior."""

from dataclasses import dataclass, field
from enum import IntFlag, auto
from functools import singledispatchmethod

from m2isar.metamodel import arch, behav
from m2isar.metamodel.utils.ExprVisitor import ExprVisitor

# pylint: disable=unused-argument


class Mode(IntFlag):
    NONE = 0
    REG = auto()
    IMM = auto()
    CONST = auto()
    IMM_CONST = IMM | CONST


@dataclass
class Result:
    """Result of visiting one expression subtree."""

    mode: Mode = Mode.NONE
    imm_names: set[str] = field(default_factory=set)

    def __or__(self, other):
        if not isinstance(other, Result):
            return NotImplemented

        return Result(
            mode=self.mode | other.mode,
            imm_names=self.imm_names | other.imm_names,
        )

    def __ior__(self, other):
        if not isinstance(other, Result):
            return NotImplemented

        self.mode |= other.mode
        self.imm_names |= other.imm_names
        return self


def combine(results):
    """Combine visitor results."""
    result = Result()
    for item in results:
        result |= item
    return result


class DetectImmLeafsVisitor(ExprVisitor):
    """Detect operand leaves used as immediate values."""

    @singledispatchmethod
    def generate(self, expr: behav.BaseNode, context):
        raise NotImplementedError(
            f"No visit method implemented for type {type(expr).__name__} in {type(self).__name__}"
        )

    @generate.register
    def _(self, expr: behav.Operation, context):
        return combine(
            self.generate(stmt, context)
            for stmt in expr.statements
        )

    @generate.register
    def _(self, expr: behav.Block, context):
        results = []

        for stmt in expr.statements:
            result = self.generate(stmt, context)

            # Keep the old empty-conditional handling if needed.
            #
            # Note that generate() returns Result now, not an AST node, so
            # checking isinstance(result, behav.Conditional) would no longer
            # make sense here.
            results.append(result)

        return combine(results)

    @generate.register
    def _(self, expr: behav.BinaryOperation, context):
        left = self.generate(expr.left, context)
        right = self.generate(expr.right, context)

        #
        # Detect exactly one unresolved immediate combined with a constant.
        #
        # This deliberately checks the two child results separately rather
        # than checking only:
        #
        #     (left | right).mode == Mode.IMM_CONST
        #
        # Otherwise expressions containing multiple immediates could collapse
        # into the same IMM bit and all of them could accidentally be marked
        # as leaves.
        #

        if (
            left.mode == Mode.IMM
            and len(left.imm_names) == 1
            and right.mode == Mode.CONST
        ):
            context.imm_leaf_names.update(left.imm_names)
            return Result()

        if (
            right.mode == Mode.IMM
            and len(right.imm_names) == 1
            and left.mode == Mode.CONST
        ):
            context.imm_leaf_names.update(right.imm_names)
            return Result()

        return left | right

    @generate.register
    def _(self, expr: behav.SliceOperation, context):
        expr_ = self.generate(expr.expr, context)
        left = self.generate(expr.left, context)
        right = self.generate(expr.right, context)
        return expr_ | left | right

    @generate.register
    def _(self, expr: behav.ConcatOperation, context):
        left = self.generate(expr.left, context)
        right = self.generate(expr.right, context)
        return left | right

    @generate.register
    def _(self, expr: behav.Literal, context):
        return Result(mode=Mode.CONST)

    @generate.register
    def _(self, expr: behav.Tensor, context):
        return Result(mode=Mode.CONST)

    @generate.register
    def _(self, expr: behav.VarDefinition, context):
        return Result()

    @generate.register
    def _(self, expr: behav.Break, context):
        return Result()

    @generate.register
    def _(self, expr: behav.Assignment, context):
        target = self.generate(expr.target, context)
        expr_ = self.generate(expr.expr, context)
        return target | expr_

    @generate.register
    def _(self, expr: behav.Conditional, context):
        conds = [
            self.generate(cond, context)
            for cond in expr.conds
        ]

        stmts = [
            self.generate(stmt, context)
            for stmt in expr.stmts
        ]

        return combine(conds + stmts)

    @generate.register
    def _(self, expr: behav.Loop, context):
        cond = self.generate(expr.cond, context)

        stmts = [
            self.generate(stmt, context)
            for stmt in expr.stmts
        ]

        return combine([cond] + stmts)

    @generate.register
    def _(self, expr: behav.Ternary, context):
        cond = self.generate(expr.cond, context)
        then_expr = self.generate(expr.then_expr, context)
        else_expr = self.generate(expr.else_expr, context)

        return cond | then_expr | else_expr

    @generate.register
    def _(self, expr: behav.Return, context):
        if expr.expr is None:
            return Result()

        return self.generate(expr.expr, context)

    @generate.register
    def _(self, expr: behav.UnaryOperation, context):
        right = self.generate(expr.right, context)

        #
        # Preserve the old behavior conceptually:
        # if the operand subtree already represents IMM + CONST, mark its
        # unresolved immediate as a leaf.
        #
        # Usually BinaryOperation will already consume simple forms such as:
        #
        #     -(imm + 4)
        #
        # so this mainly handles cases where IMM_CONST survives from another
        # node type.
        #
        if (
            right.mode == Mode.IMM_CONST
            and len(right.imm_names) == 1
        ):
            context.imm_leaf_names.update(right.imm_names)
            return Result()

        return right

    @generate.register
    def _(self, expr: behav.NamedReference, context):
        if isinstance(expr.reference, arch.BitFieldDescr):
            if expr.reference.name in context.imm_op_names:
                return Result(
                    mode=Mode.IMM,
                    imm_names={expr.reference.name},
                )

            return Result(mode=Mode.REG)

        return Result()

    @generate.register
    def _(self, expr: behav.IndexedReference, context):
        if isinstance(expr.reference, (arch.Memory, arch.RegisterBank)):
            return self.generate(expr.index, context)

        return Result()

    @generate.register
    def _(self, expr: behav.TypeConv, context):
        return self.generate(expr.expr, context)

    @generate.register
    def _(self, expr: behav.Callable, context):
        return combine(
            self.generate(arg, context)
            for arg in expr.args
        )

    @generate.register
    def _(self, expr: behav.Group, context):
        return self.generate(expr.expr, context)

    @generate.register
    def _(self, expr: behav.ProcedureCall, context):
        return combine(
            self.generate(arg, context)
            for arg in expr.args
        )

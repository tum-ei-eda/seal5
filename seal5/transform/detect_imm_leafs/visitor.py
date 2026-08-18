# SPDX-License-Identifier: Apache-2.0
#
# This file is part of the M2-ISA-R project: https://github.com/tum-ei-eda/M2-ISA-R
#
# Copyright (C) 2022
# Chair of Electrical Design Automation
# Technical University of Munich

"""Detect immediate-value leaves within instruction behavior."""

from enum import IntFlag, auto
from functools import reduce, singledispatchmethod

from m2isar.metamodel import arch, behav
from m2isar.metamodel.utils.ExprVisitor import ExprVisitor

# pylint: disable=unused-argument


class Mode(IntFlag):
    NONE = 0
    REG = auto()
    IMM = auto()
    CONST = auto()
    IMM_CONST = IMM | CONST


class DetectImmLeafsVisitor(ExprVisitor):
    """Detect operand leaves used as immediate values."""

    @singledispatchmethod
    def generate(self, expr: behav.BaseNode, context):
        raise NotImplementedError(
            f"No visit method implemented for type {type(expr).__name__} in {type(self).__name__}"
        )

    @generate.register
    def _(self, expr: behav.Operation, context):
        stmts = []
        for stmt in expr.statements:
            temp = self.generate(stmt, context)
            if isinstance(temp, list):
                stmts.extend(temp)
            else:
                stmts.append(temp)
        return reduce(lambda x, y: x | y, stmts) if len(stmts) > 0 else Mode.NONE

    @generate.register
    def _(self, expr: behav.Block, context):
        stmts = []
        for stmt in expr.statements:
            stmt = self.generate(stmt, context)
            if isinstance(stmt, behav.Conditional):
                if len(stmt.conds) == 1 and isinstance(stmt.stmts[0], behav.Block) and len(stmt.stmts[0].statements) == 0:
                    continue
            stmts.append(stmt)
        return reduce(lambda x, y: x | y, stmts) if len(stmts) > 0 else Mode.NONE

    @generate.register
    def _(self, expr: behav.BinaryOperation, context):
        left = self.generate(expr.left, context)
        right = self.generate(expr.right, context)
        if (left | right) == Mode.IMM_CONST:
            assert context.last_imm_name is not None
            context.imm_leaf_names.add(context.last_imm_name)
            context.last_imm_name = None
            return Mode.NONE
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
        return Mode.CONST

    @generate.register
    def _(self, expr: behav.VarDefinition, context):
        return Mode.NONE

    @generate.register
    def _(self, expr: behav.Break, context):
        return Mode.NONE

    @generate.register
    def _(self, expr: behav.Assignment, context):
        target = self.generate(expr.target, context)
        expr_ = self.generate(expr.expr, context)
        return target | expr_

    @generate.register
    def _(self, expr: behav.Conditional, context):
        conds = [self.generate(cond, context) for cond in expr.conds]
        stmts = [self.generate(op, context) for op in expr.stmts]
        return reduce(lambda x, y: x | y, conds + stmts)

    @generate.register
    def _(self, expr: behav.Loop, context):
        cond = self.generate(expr.cond, context)
        stmts = [self.generate(x, context) for x in expr.stmts]
        return reduce(lambda x, y: x | y, [cond] + stmts)

    @generate.register
    def _(self, expr: behav.Ternary, context):
        cond = self.generate(expr.cond, context)
        then_expr = self.generate(expr.then_expr, context)
        else_expr = self.generate(expr.else_expr, context)
        return cond | then_expr | else_expr

    @generate.register
    def _(self, expr: behav.Return, context):
        return self.generate(expr.expr, context) if expr.expr is not None else Mode.NONE

    @generate.register
    def _(self, expr: behav.UnaryOperation, context):
        right = self.generate(expr.right, context)
        if right == Mode.IMM_CONST:
            assert context.last_imm_name is not None
            context.imm_leaf_names.add(context.last_imm_name)
            context.last_imm_name = None
            return Mode.NONE
        return right

    @generate.register
    def _(self, expr: behav.NamedReference, context):
        if isinstance(expr.reference, arch.BitFieldDescr):
            if expr.reference.name in context.imm_op_names:
                context.last_imm_name = expr.reference.name
                return Mode.IMM
            return Mode.REG
        return Mode.NONE

    @generate.register
    def _(self, expr: behav.IndexedReference, context):
        if isinstance(expr.reference, (arch.Memory, arch.RegisterBank)):
            return self.generate(expr.index, context)
        return Mode.NONE

    @generate.register
    def _(self, expr: behav.TypeConv, context):
        return self.generate(expr.expr, context)

    @generate.register
    def _(self, expr: behav.Callable, context):
        args = [self.generate(stmt, context) for stmt in expr.args]
        return reduce(lambda x, y: x | y, args) if args else Mode.NONE

    @generate.register
    def _(self, expr: behav.Group, context):
        return self.generate(expr.expr, context)

    @generate.register
    def _(self, expr: behav.ProcedureCall, context):
        fn_args = [self.generate(arg, context) for arg in expr.args]
        return reduce(lambda x, y: x | y, fn_args) if fn_args else Mode.NONE

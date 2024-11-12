# SPDX-License-Identifier: Apache-2.0
#
# This file is part of the M2-ISA-R project: https://github.com/tum-ei-eda/M2-ISA-R
#
# Copyright (C) 2022
# Chair of Electrical Design Automation
# Technical University of Munich

"""TODO"""
from functools import reduce

from enum import IntFlag, auto

from m2isar.metamodel import arch, behav

# pylint: disable=unused-argument

# Limitations
# - Keep the condition stack as small as possible (move raise to highest level of behavior)
# - If block should only have a call to raise
# - Standalone if statements (without else/else if) are preferred
# - Raise calls are replaced by empty blocks, to be removed in the operation visitor
# - ~~Run optimizer afterwards to eliminate if statement.~~


class Mode(IntFlag):
    NONE = 0
    REG = auto()
    IMM = auto()
    CONST = auto()
    IMM_CONST = IMM | CONST


def operation(self: behav.Operation, context):
    # print("operation", self)
    statements = []
    for stmt in self.statements:
        temp = stmt.generate(context)
        if isinstance(temp, list):
            for _t in temp:
                pass
                # print("t", t, type(t), dir(t))
            statements.extend(temp)
        else:
            # print("temp", temp, type(temp), dir(temp))
            statements.append(temp)
    # input("eeeee")

    return reduce(lambda x, y: x | y, statements)


def block(self: behav.Block, context):
    # print("block")

    stmts = []

    for stmt in self.statements:
        stmt = stmt.generate(context)
        if isinstance(stmt, behav.Conditional):
            if len(stmt.conds) == 1:
                if isinstance(stmt.stmts[0], behav.Block):
                    if len(stmt.stmts[0].statements) == 0:
                        continue
        stmts.append(stmt)

    return reduce(lambda x, y: x | y, stmts) if len(stmts) > 0 else Mode.NONE


def binary_operation(self: behav.BinaryOperation, context):
    # print("binary_operation {")
    left = self.left.generate(context)
    right = self.right.generate(context)
    # print("left", left)
    # print("right", right)
    # print("left | right", left | right)
    # print("(left | right) == IMM_CONST", (left | right) == Mode.IMM_CONST)
    if (left | right) == Mode.IMM_CONST:
        assert context.last_imm_name is not None
        context.imm_leaf_names.add(context.last_imm_name)
        context.last_imm_name = None
        return Mode.NONE
    # input("} binary_operation")

    return left | right


def slice_operation(self: behav.SliceOperation, context):
    # print("slice_operation")
    expr = self.expr.generate(context)
    left = self.left.generate(context)
    right = self.right.generate(context)

    return expr | left | right


def concat_operation(self: behav.ConcatOperation, context):
    # print("concat_operation")
    left = self.left.generate(context)
    right = self.right.generate(context)

    return left | right


def number_literal(self: behav.IntLiteral, context):
    # print("number_literal")
    return Mode.CONST


def int_literal(self: behav.IntLiteral, context):
    # print("int_literal")
    return Mode.CONST


def scalar_definition(self: behav.ScalarDefinition, context):
    # print("scalar_definition")
    return Mode.NONE


def break_(self: behav.Break, context):
    # print("break")
    return Mode.NONE


def assignment(self: behav.Assignment, context):
    # print("assignment")
    target = self.target.generate(context)
    expr = self.expr.generate(context)

    return target | expr


def conditional(self: behav.Conditional, context):
    # print("conditional")
    conds = []
    for i, cond in enumerate(self.conds):
        cond_ = cond.generate(context)
        conds.append(cond_)
    stmts = []
    for op in self.stmts:
        # for stmt in flatten(op):
        #    stmt.generate(context)
        stmt = op.generate(context)
        stmts.append(stmt)

    return reduce(lambda x, y: x | y, conds + stmts)


def loop(self: behav.Loop, context):
    # print("loop")
    cond = self.cond.generate(context)
    stmts = [x.generate(context) for x in self.stmts]

    return reduce(lambda x, y: x | y, [cond] + stmts)


def ternary(self: behav.Ternary, context):
    # print("ternary")
    cond = self.cond.generate(context)
    then_expr = self.then_expr.generate(context)
    else_expr = self.else_expr.generate(context)

    return cond | then_expr | else_expr


def return_(self: behav.Return, context):
    # print("return_")
    expr = Mode.NONE
    if self.expr is not None:
        expr = self.expr.generate(context)

    return expr


def unary_operation(self: behav.UnaryOperation, context):
    # print("unary_operation {")
    right = self.right.generate(context)
    # print("right", right)
    # print("right == IMM_CONST", right == Mode.IMM_CONST)
    # input("} unary_operation")
    if right == Mode.IMM_CONST:
        assert context.last_imm_name is not None
        context.imm_leaf_names.add(context.last_imm_name)
        context.last_imm_name = None
        return Mode.NONE

    return right


def named_reference(self: behav.NamedReference, context):
    # print("named_reference")
    # print("name", self.reference.name)
    # TODO: hanlde constant and scalar!
    if isinstance(self.reference, arch.BitFieldDescr):
        # print("if")
        if self.reference.name in context.imm_op_names:
            # print("if if")
            # input(">>>")
            context.last_imm_name = self.reference.name
            return Mode.IMM
        else:
            return Mode.REG
    # print("return None")
    return Mode.NONE


def indexed_reference(self: behav.IndexedReference, context):
    # print("indexed_reference")
    assert isinstance(self.reference, arch.Memory)
    # name = self.reference.name

    index = self.index.generate(context)
    return index


def type_conv(self: behav.TypeConv, context):
    # print("type_conv {")
    expr = self.expr.generate(context)
    # print("expr", expr)
    # input("} type_conv")

    return expr


def callable_(self: behav.Callable, context):
    # print("callable")
    args = [stmt.generate(context) for stmt in self.args]

    return reduce(lambda x, y: x | y, args)


def group(self: behav.Group, context):
    # print("group {")
    expr = self.expr.generate(context)
    # print("expr", expr)
    # input("} group")

    return expr


def procedure_call(self: behav.ProcedureCall, context):
    # print("procedure_call")

    fn_args = [arg.generate(context) for arg in self.args]

    return reduce(lambda x, y: x | y, fn_args)

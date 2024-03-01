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

# Limitations
# - Keep the condition stack as small as possible (move raise to highest level of behavior)
# - If block should only have a call to raise
# - Standalone if statements (without else/else if) are preferred
# - Raise calls are replaced by empty blocks, to be removed in the operation visitor
# - ~~Run optimizer afterwards to eliminate if statement.~~


def operation(self: behav.Operation, context):
    # print("operation", self)
    statements = []
    for stmt in self.statements:
        temp = stmt.generate(context)
        if isinstance(temp, list):
            for t in temp:
                pass
                # print("t", t, type(t), dir(t))
            statements.extend(temp)
        else:
            # print("temp", temp, type(temp), dir(temp))
            statements.append(temp)
    # input("eeeee")

    self.statements = statements
    return self


def block(self: behav.Block, context):
    # print("block", self)

    stmts = []

    for stmt in self.statements:
        stmt = stmt.generate(context)
        if isinstance(stmt, behav.Conditional):
            if len(stmt.conds) == 1:
                if isinstance(stmt.stmts[0], behav.Block):
                    if len(stmt.stmts[0].statements) == 0:
                        continue
        stmts.append(stmt)

    self.statements = stmts

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
    # print("assignment")
    context.is_write = True
    self.target = self.target.generate(context)
    context.is_write = False
    context.is_read = True
    self.expr = self.expr.generate(context)
    context.is_read = False

    return self


def conditional(self: behav.Conditional, context):
    # print("conditional")
    for i, cond in enumerate(self.conds):
        context.is_read = True
        self.conds[i] = cond.generate(context)
        context.is_read = False
    for op in self.stmts:
        # for stmt in flatten(op):
        #    stmt.generate(context)
        op.generate(context)

    return self


def loop(self: behav.Loop, context):
    context.is_read = True
    self.cond = self.cond.generate(context)
    context.is_read = False
    self.stmts = [x.generate(context) for x in self.stmts]

    return self


def ternary(self: behav.Ternary, context):
    context.is_read = True
    self.cond = self.cond.generate(context)
    context.is_read = False
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
    # print("indexed_reference")
    assert isinstance(self.reference, arch.Memory)
    # name = self.reference.name
    if arch.MemoryAttribute.IS_MAIN_MEM in self.reference.attributes:
        if context.is_write:
            context.may_store = True
        elif context.is_read:
            context.may_load = True
    else:
        pass  # TODO

    self.index = self.index.generate(context)
    return self


def type_conv(self: behav.TypeConv, context):
    self.expr = self.expr.generate(context)

    return self


def callable_(self: behav.Callable, context):
    self.args = [stmt.generate(context) for stmt in self.args]

    return self


def group(self: behav.Group, context):
    # print("group", group)
    self.expr = self.expr.generate(context)

    return self


def procedure_call(self: behav.ProcedureCall, context):
    # print("procedure_call")

    self.fn_args = [arg.generate(context) for arg in self.args]

    return self

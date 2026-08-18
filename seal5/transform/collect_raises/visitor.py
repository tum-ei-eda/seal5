# SPDX-License-Identifier: Apache-2.0
#
# This file is part of the M2-ISA-R project: https://github.com/tum-ei-eda/M2-ISA-R
#
# Copyright (C) 2022
# Chair of Electrical Design Automation
# Technical University of Munich

"""Collect raise constraints from behavior expressions."""

from functools import singledispatchmethod

from m2isar.metamodel import arch, behav
from m2isar.metamodel.utils.ExprVisitor import ExprVisitor

# pylint: disable=unused-argument

# Limitations
# - Keep the condition stack as small as possible (move raise to highest level of behavior)
# - If block should only have a call to raise
# - Standalone if statements (without else/else if) are preferred
# - Raise calls are replaced by empty blocks, to be removed in the operation visitor
# - ~~Run optimizer afterwards to eliminate if statement.~~


class CollectRaisesVisitor(ExprVisitor):
    """Collect raise constraints from behavioral expressions."""

    @singledispatchmethod
    def generate(self, expr: behav.BaseNode, context):
        raise NotImplementedError(
            f"No visit method implemented for type "
            f"{type(expr).__name__} in {type(self).__name__}"
        )


    @generate.register
    def _(self, expr: behav.Operation, context):
        # print("operation", self)
        statements = []
        for stmt in expr.statements:
            temp = self.generate(stmt, context)
            if isinstance(temp, list):
                # for t in temp:
                # print("t", t, type(t), dir(t))
                statements.extend(temp)
            else:
                # print("temp", temp, type(temp), dir(temp))
                statements.append(temp)
        # input("eeeee")

        expr.statements = statements
        return expr


    @generate.register
    def _(self, expr: behav.Block, context):
        # print("block", self)

        stmts = []

        for stmt in expr.statements:
            stmt = self.generate(stmt, context)
            if isinstance(stmt, behav.Conditional):
                if len(stmt.conds) == 1:
                    if isinstance(stmt.stmts[0], behav.Block):
                        if len(stmt.stmts[0].statements) == 0:
                            continue
            stmts.append(stmt)

        expr.statements = stmts

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
        # print("conditional")
        expr.conds = [self.generate(x, context) for x in expr.conds]
        # expr.stmts = [x.generate(context) for x in expr.stmts]
        temp = []
        for i, stmt in enumerate(expr.stmts):
            if i == 0:  # if
                cond = expr.conds[i]
                temp.append(behav.UnaryOperation(behav.Operator("!"), cond))
            elif i < len(expr.conds):  # elif
                cond = temp[0]
                for c in temp[1:]:
                    cond = behav.BinaryOperation(cond, "&&", c)
                cond = behav.BinaryOperation(cond, "&&", expr.conds[i])
            else:  # else
                assert i >= len(expr.conds)
                assert len(temp) >= 1
                cond = temp[0]
                for c in temp[1:]:
                    cond = behav.BinaryOperation(cond, "&&", c)
            context.cond_stack.append(cond)
            # print("before", context.cond_stack)
            stmt = self.generate(stmt, context)
            if context.found_raise:
                # print("stmt", stmt, dir(stmt))
                if isinstance(stmt, behav.Block):
                    # print("block.statements", stmt.statements)
                    assert len(stmt.statements) == 1, "Raise block may only have a single operation"
                    assert isinstance(stmt.statements[0], behav.ProcedureCall), "Nesting raises not allowed"
                    assert isinstance(stmt.statements[0].ref_or_name, arch.Function), "Expected function"
                    assert stmt.statements[0].ref_or_name.name == "raise", "Expected raise operation"
                    stmt = behav.Block([])  # Replace with empty block
                    context.found_raise = False
                else:
                    assert isinstance(stmt, behav.ProcedureCall), "Nesting raises not allowed"
                    assert isinstance(stmt.ref_or_name, arch.Function), "Expected function"
                    assert stmt.ref_or_name.name == "raise", "Expected raise operation"
                    stmt = behav.Block([])  # Replace with empty block
                    context.found_raise = False
                # input("aaaa")
            expr.stmts[i] = stmt
            # print("after", context.cond_stack)
            context.cond_stack.pop()
        # print("expr.stmts", expr.stmts)

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
        return expr


    @generate.register
    def _(self, expr: behav.IndexedReference, context):
        expr.index = self.generate(expr.index, context)

        return expr


    @generate.register
    def _(self, expr: behav.TypeConv, context):
        expr.expr = self.generate(expr.expr, context)

        return expr


    @generate.register
    def _(self, expr: behav.Callable, context):
        expr.args = [self.generate(arg, context) for arg in expr.args]

        return expr


    @generate.register
    def _(self, expr: behav.Group, context):
        # print("group", group)
        expr.expr = self.generate(expr.expr, context)

        return expr


    @generate.register
    def _(self, expr: behav.ProcedureCall, context):
        # print("procedure_call")

        fn_args = [self.generate(arg, context) for arg in expr.args]

        # extract function object reference
        ref = expr.ref_or_name if isinstance(expr.ref_or_name, arch.Function) else None
        name = ref.name if isinstance(expr.ref_or_name, arch.Function) else expr.ref_or_name
        # print("name", name)
        # print("args", fn_args)
        if name == "raise":
            args = [arg.value for arg in fn_args]
            if len(context.cond_stack) == 0:
                cond = None
            else:
                cond = context.cond_stack[-1]
                # for c in context.cond_stack[1:]:
                cond = behav.UnaryOperation(behav.Operator("!"), behav.Group(cond))
                # TODO: transform !(imm % 4) -> !(imm % 4 != 0) -> imm % 4 == 0
            context.raises.append((cond, args))
            context.found_raise = True
            # input("qqqq")
        return expr

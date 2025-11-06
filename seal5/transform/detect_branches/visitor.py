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


def peek(item):
    if isinstance(item, behav.Group):
        return item.expr
    return item


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

    self.statements = statements
    return self


def block(self: behav.Block, context):
    print("block", self)

    stmts = []

    for stmt in self.statements:
        stmt = stmt.generate(context)
        if isinstance(stmt, behav.Conditional):
            if len(stmt.conds) == 1:
                if isinstance(stmt.stmts[0], behav.Block):
                    if len(stmt.stmts) == 1:
                        if len(stmt.stmts[0].statements) == 0:
                            continue
                    elif len(stmt.stmts) == 2:
                        if len(stmt.stmts[0].statements) == 0 and len(stmt.stmts[1].statements) == 0:
                            continue
        stmts.append(stmt)

    self.statements = stmts
    print("self.statements", self.statements)

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
    print("assignment")
    print("target", self.target)
    print("expr", self.expr)
    pc_mem = None
    if isinstance(self.target, behav.NamedReference) and self.target.reference.name == "PC":
        print("write pc")
        context.writes_pc = True
        pc_mem = self.target.reference
    else:
        self.target = self.target.generate(context)
    print("pc_mem", pc_mem)
    if pc_mem is not None:
        expr_ = self.expr
        if isinstance(expr_, behav.SliceOperation):
            if (
                isinstance(expr_.left, behav.IntLiteral)
                and expr_.left.value == (pc_mem.size - 1)
                and isinstance(expr_.right, behav.IntLiteral)
                and expr_.right.value == 0
            ):
                expr_ = peek(expr_.expr)
                print("if12", expr_)
        if isinstance(expr_, behav.BinaryOperation):
            print("binop expr", expr_, expr_.op)
            left = peek(expr_.left)
            right = peek(expr_.right)
            op = expr_.op
            print("left", left)
            print("right", right)
            print("op.value", op.value)
            if op.value == "+" and isinstance(left, behav.NamedReference) and self.target.reference.name == "PC":
                base = left
                offset = right
                print(context.cond_stack)
                if len(context.cond_stack) == 1:
                    cond = context.cond_stack[0]
                    print("cond", cond)
                    print("base", base)
                    print("offset", offset)
                    branch_call = behav.ProcedureCall("branch", [cond, offset])
                    print("branch_call", branch_call)
                    return branch_call
        else:
            self.expr = self.expr.generate(context)

    return self


def conditional(self: behav.Conditional, context):
    print("conditional")
    self.conds = [x.generate(context) for x in self.conds]
    # self.stmts = [x.generate(context) for x in self.stmts]
    temp = []
    print("self.stmts", self, self.stmts)
    for i, stmt in enumerate(self.stmts):
        print("i", i)
        cond_ = self.conds[i]
        if i == 0:  # if
            print("if stmt", stmt)
            cond = cond_
            temp.append(behav.UnaryOperation(behav.Operator("!"), cond_))
        elif i < len(self.conds):  # elif
            print("elif stmt", stmt)
            cond = temp[0]
            for c in temp[1:]:
                cond = behav.BinaryOperation(cond, "&&", c)
            cond = behav.BinaryOperation(cond, "&&", cond_)
        else:  # else
            print("else stmt", stmt)
            assert i >= len(self.conds)
            assert len(temp) >= 1
            cond = temp[0]
            for c in temp[1:]:
                cond = behav.BinaryOperation(cond, "&&", c)
        context.cond_stack.append(cond)
        print("stmt", stmt)
        stmt = stmt.generate(context)
        print("stmt2", stmt)
        print("context.found_branch", context.found_branch)
        print("context.uses_pc", context.uses_pc)
        # if context.uses_pc:
        if context.found_branch:
            raise NotImplementedError("TODO")
        self.stmts[i] = stmt
        if i < len(self.conds):
            self.conds[i] = cond_
        # print("after", context.cond_stack)
        context.cond_stack.pop()
    print("self.stmts2", self, self.stmts)

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
    # print("named_reference", self.reference)
    if self.reference.name == "PC":
        context.reads_pc = True
    return self


def indexed_reference(self: behav.IndexedReference, context):
    # print("indexed_reference")
    assert isinstance(self.reference, arch.Memory)
    # name = self.reference.name

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
    print("procedure_call")

    self.fn_args = [arg.generate(context) for arg in self.args]

    return self

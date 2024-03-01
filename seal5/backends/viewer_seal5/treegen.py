# SPDX-License-Identifier: Apache-2.0
#
# This file is part of the M2-ISA-R project: https://github.com/tum-ei-eda/M2-ISA-R
#
# Copyright (C) 2022
# Chair of Electrical Design Automation
# Technical University of Munich

"""Generate a ttk.Treeview representation of a M2-ISA-R model structure."""

# import tkinter as tk

from ...metamodel import behav
from .utils import TreeGenContext

# pylint: disable=unused-argument


def operation(self: behav.Operation, context: "TreeGenContext"):
    context.insert("Operation")
    print("operation", self.statements)

    for stmt in self.statements:
        if stmt is None:
            continue
        stmt.generate(context)

    context.pop()


def block(self: behav.Block, context: "TreeGenContext"):
    context.insert("Block")

    for stmt in self.statements:
        if stmt is None:
            continue
        stmt.generate(context)

    context.pop()


def binary_operation(self: behav.BinaryOperation, context: "TreeGenContext"):
    context.insert("Binary Operation")

    context.insert("Left")
    self.left.generate(context)
    context.pop()

    context.insert("Right")
    self.right.generate(context)
    context.pop()

    context.insert2("Op", values=(self.op.value,))

    context.pop()


def slice_operation(self: behav.SliceOperation, context: "TreeGenContext"):
    context.insert("Slice Operation")

    context.insert("Expr")
    self.expr.generate(context)
    context.pop()

    context.insert("Left")
    self.left.generate(context)
    context.pop()

    context.insert("Right")
    self.right.generate(context)
    context.pop()

    context.pop()


def concat_operation(self: behav.ConcatOperation, context: "TreeGenContext"):
    context.insert("Concat Operation")

    context.insert("Left")
    self.left.generate(context)
    context.pop()

    context.insert("Right")
    self.right.generate(context)
    context.pop()

    context.pop()


def number_literal(self: behav.IntLiteral, context: "TreeGenContext"):
    context.insert2("Number Literal", values=(self.value,))


def int_literal(self: behav.IntLiteral, context: "TreeGenContext"):
    context.insert2("Int Literal", values=(self.value,))


def scalar_definition(self: behav.ScalarDefinition, context: "TreeGenContext"):
    context.insert2("Scalar Definition", values=(self.scalar.name,))


def break_(self: behav.Break, context: "TreeGenContext"):
    context.insert2("Break")


def assignment(self: behav.Assignment, context: "TreeGenContext"):
    context.insert("Assignment")

    context.insert("Target")
    self.target.generate(context)
    context.pop()

    context.insert("Expr")
    self.expr.generate(context)
    context.pop()

    context.pop()


def conditional(self: behav.Conditional, context: "TreeGenContext"):
    context.insert("Conditional")

    context.insert("Conditions")
    for cond in self.conds:
        cond.generate(context)
    context.pop()

    context.insert("Statements")
    for stmt in self.stmts:
        if stmt is None:
            continue
        stmt.generate(context)
    context.pop()

    context.pop()


def loop(self: behav.Loop, context: "TreeGenContext"):
    context.insert("Loop")

    context.insert2("Post Test", values=(self.post_test,))

    context.insert("Condition")
    self.cond.generate(context)
    context.pop()

    context.insert("Statements")
    for stmt in self.stmts:
        stmt.generate(context)
    context.pop()

    context.pop()


def ternary(self: behav.Ternary, context: "TreeGenContext"):
    context.insert("Ternary")

    context.insert("Cond")
    self.cond.generate(context)
    context.pop()

    context.insert("Then Expression")
    self.then_expr.generate(context)
    context.pop()

    context.insert("Else Expression")
    self.else_expr.generate(context)
    context.pop()

    context.pop()


def return_(self: behav.Return, context: "TreeGenContext"):
    context.insert("Return")

    if self.expr is not None:
        context.insert("Expression")
        self.expr.generate(context)
        context.pop()

    context.pop()


def unary_operation(self: behav.UnaryOperation, context: "TreeGenContext"):
    context.insert("Unary Operation")

    context.insert("Right")
    self.right.generate(context)
    context.pop()

    context.insert2("Op", values=(self.op.value,))

    context.pop()


def named_reference(self: behav.NamedReference, context: "TreeGenContext"):
    context.insert2("Named Reference", values=(f"{self.reference}",))


def indexed_reference(self: behav.IndexedReference, context: "TreeGenContext"):
    context.insert("Indexed Reference")

    context.insert2("Reference", values=(f"{self.reference}",))

    context.insert("Index")
    self.index.generate(context)
    context.pop()

    context.pop()


def type_conv(self: behav.TypeConv, context: "TreeGenContext"):
    context.insert("Type Conv")

    context.insert2("Type", values=(self.data_type,))
    context.insert2("Size", values=(self.size,))

    context.insert("Expr")
    self.expr.generate(context)
    context.pop()

    context.pop()


def callable_(self: behav.Callable, context: "TreeGenContext"):
    context.insert("Callable", values=(self.ref_or_name.name,))

    for arg, arg_descr in zip(self.args, self.ref_or_name.args):
        context.insert("Arg", values=(arg_descr,))
        arg.generate(context)
        context.pop()

    context.pop()


def group(self: behav.Group, context: "TreeGenContext"):
    context.insert("Group")

    context.insert("Expr")
    self.expr.generate(context)
    context.pop()

    context.pop()

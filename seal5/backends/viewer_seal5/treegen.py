# SPDX-License-Identifier: Apache-2.0
#
# This file is part of the M2-ISA-R project: https://github.com/tum-ei-eda/M2-ISA-R
#
# Copyright (C) 2022
# Chair of Electrical Design Automation
# Technical University of Munich

"""Generate a ttk.Treeview representation of current M2-ISA-R behavior."""

from functools import singledispatchmethod

from m2isar.metamodel import behav
from m2isar.metamodel.utils.ExprVisitor import ExprVisitor

from .utils import TreeGenContext


class TreeGenVisitor(ExprVisitor):
    """Render M2-ISA-R behavior nodes into a tree-generation context."""

    @singledispatchmethod
    def generate(self, expr: behav.BaseNode, context: TreeGenContext):
        context.insert2(type(expr).__name__, values=(str(expr),))

    @generate.register
    def _(self, expr: behav.Operation, context: TreeGenContext):
        self._render_statements("Operation", expr.statements, context)

    @generate.register
    def _(self, expr: behav.Block, context: TreeGenContext):
        self._render_statements("Block", expr.statements, context)

    @generate.register
    def _(self, expr: behav.Literal, context: TreeGenContext):
        context.insert2("Literal", values=(expr.value,))

    @generate.register
    def _(self, expr: behav.Tensor, context: TreeGenContext):
        context.insert2("Tensor", values=(expr.value,))

    @generate.register
    def _(self, expr: behav.VarDefinition, context: TreeGenContext):
        context.insert2("Variable Definition", values=(expr.var.name,))

    @generate.register
    def _(self, expr: behav.Break, context: TreeGenContext):
        context.insert2("Break")

    @generate.register
    def _(self, expr: behav.Assignment, context: TreeGenContext):
        context.insert("Assignment")
        self._render_child("Target", expr.target, context)
        self._render_child("Expr", expr.expr, context)
        context.pop()

    @generate.register
    def _(self, expr: behav.BinaryOperation, context: TreeGenContext):
        context.insert("Binary Operation")
        self._render_child("Left", expr.left, context)
        self._render_child("Right", expr.right, context)
        context.insert2("Op", values=(expr.op.value,))
        context.pop()

    @generate.register
    def _(self, expr: behav.SliceOperation, context: TreeGenContext):
        context.insert("Slice Operation")
        self._render_child("Expr", expr.expr, context)
        self._render_child("Left", expr.left, context)
        self._render_child("Right", expr.right, context)
        context.pop()

    @generate.register
    def _(self, expr: behav.ConcatOperation, context: TreeGenContext):
        context.insert("Concat Operation")
        self._render_child("Left", expr.left, context)
        self._render_child("Right", expr.right, context)
        context.pop()

    @generate.register
    def _(self, expr: behav.UnaryOperation, context: TreeGenContext):
        context.insert("Unary Operation")
        self._render_child("Right", expr.right, context)
        context.insert2("Op", values=(expr.op.value,))
        context.pop()

    @generate.register
    def _(self, expr: behav.NamedReference, context: TreeGenContext):
        context.insert2("Named Reference", values=(str(expr.reference),))

    @generate.register
    def _(self, expr: behav.IndexedReference, context: TreeGenContext):
        context.insert("Indexed Reference")
        context.insert2("Reference", values=(str(expr.reference),))
        self._render_child("Index", expr.index, context)
        if expr.right is not None:
            self._render_child("Right", expr.right, context)
        context.pop()

    @generate.register
    def _(self, expr: behav.TypeConv, context: TreeGenContext):
        context.insert("Type Conv")
        context.insert2("Type", values=(expr.data_type,))
        context.insert2("Size", values=(expr.size,))
        self._render_child("Expr", expr.expr, context)
        context.pop()

    @generate.register
    def _(self, expr: behav.Conditional, context: TreeGenContext):
        context.insert("Conditional")
        self._render_children("Conditions", expr.conds, context)
        self._render_children("Statements", expr.stmts, context)
        context.pop()

    @generate.register
    def _(self, expr: behav.Loop, context: TreeGenContext):
        context.insert("Loop")
        context.insert2("Post Test", values=(expr.post_test,))
        self._render_child("Condition", expr.cond, context)
        self._render_children("Statements", expr.stmts, context)
        context.pop()

    @generate.register
    def _(self, expr: behav.Ternary, context: TreeGenContext):
        context.insert("Ternary")
        self._render_child("Cond", expr.cond, context)
        self._render_child("Then Expression", expr.then_expr, context)
        self._render_child("Else Expression", expr.else_expr, context)
        context.pop()

    @generate.register
    def _(self, expr: behav.Return, context: TreeGenContext):
        context.insert("Return")
        if expr.expr is not None:
            self._render_child("Expression", expr.expr, context)
        context.pop()

    @generate.register
    def _(self, expr: behav.Callable, context: TreeGenContext):
        context.insert("Callable", values=(str(expr.ref_or_name),))
        for arg in expr.args:
            self.generate(arg, context)
        context.pop()

    @generate.register
    def _(self, expr: behav.ProcedureCall, context: TreeGenContext):
        context.insert("Procedure Call", values=(str(expr.ref_or_name),))
        for arg in expr.args:
            self.generate(arg, context)
        context.pop()

    @generate.register
    def _(self, expr: behav.Group, context: TreeGenContext):
        context.insert("Group")
        self._render_child("Expr", expr.expr, context)
        context.pop()

    def _render_statements(self, label, statements, context):
        context.insert(label)
        for statement in statements:
            if statement is not None:
                self.generate(statement, context)
        context.pop()

    def _render_child(self, label, child, context):
        context.insert(label)
        self.generate(child, context)
        context.pop()

    def _render_children(self, label, children, context):
        context.insert(label)
        for child in children:
            if child is not None:
                self.generate(child, context)
        context.pop()
